import json
import re
from functools import cache
from pathlib import Path
from typing import Any, Type

from vein_wiki_tools.clients.pakdump import get_subclass_type
from vein_wiki_tools.clients.pakdump.consumables import UEFluidDefinition
from vein_wiki_tools.clients.pakdump.firearms import UEBulletType
from vein_wiki_tools.clients.pakdump.models import (
    UEBlueprintGeneratedClass,
    UEItemType,
    UEModel,
    UEReference,
)
from vein_wiki_tools.clients.pakdump.spawnlists import UEItemList, UEItemSpawnlist
from vein_wiki_tools.clients.pakdump.tools import UETool
from vein_wiki_tools.data.models import Graph, Node
from vein_wiki_tools.errors import VeinError
from vein_wiki_tools.models.common import (
    AllConditions,
    BaseDamage,
    ClothingInfobox,
    ConditionReference,
    Construction,
    Dismantle,
    DismantleResult,
    FluidContent,
    FluidInfobox,
    FoodConditionSet,
    Infobox,
    ItemCountReference,
    ItemInfobox,
    ItemMinMaxReference,
    LinkType,
    Repair,
    Requirements,
    Scavenging,
    WeaponInfobox,
    WikiReference,
    XPGainReference,
    get_wiki_temperature_string,
    get_wiki_weight_string,
)
from vein_wiki_tools.utils.file_helper import get_vein_root
from vein_wiki_tools.utils.logging import getLogger

logger = getLogger(__name__)

VEIN_PAK_DUMP_ROOT = get_vein_root()


@cache
def get_ue_model_by_path(path: Path) -> UEModel:
    """Read the contents of a file asynchronously."""
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if not path.is_file():
        raise ValueError(f"Path is not a file: {path}")
    if not path.suffix.lower() == ".json":
        raise ValueError(f"File is not a JSON file: {path}")

    content = json.loads(path.read_text())
    if not isinstance(content, list):
        raise ValueError(f"Unexpected content format in file: {path}")

    _type = get_type(content)

    if _type is UEBlueprintGeneratedClass:
        model = content[0]
        if len(content) > 1:
            obj: dict = content[1]
            if "Template" in obj:
                template = UEReference.model_validate(obj["Template"])
                if template is None:
                    raise ValueError(
                        f"Template reference can't be handled in file: {path}"
                    )
                template_model = get_ue_model_by_reference(template)
                if not isinstance(template_model, UEBlueprintGeneratedClass):
                    raise ValueError(f"Template model is not a UEModel in file: {path}")
                if template_model.object is None:
                    raise ValueError(f"Template model has no object in file: {path}")
                temp_props = template_model.object.properties.model_dump(
                    exclude_none=True, exclude_unset=True
                )
                temp_props.update(obj.get("Properties", {}))
                obj["Properties"] = temp_props
                model["SuperStruct"] = template_model.super_struct
            model["object"] = obj
        return _type.model_validate(model)
    else:
        return _type.model_validate(content[0])


@cache
def get_ue_model_by_reference(
    model_reference: UEReference,
    _root: Path | None = None,
) -> UEModel:
    """Get a UEModel from a UEReference."""
    model_path = model_reference.object_path[:-2]  # Remove the .0 or .1 at the end
    if model_path.startswith("/Game/"):
        model_path = model_path[len("/Game/") :]
    if model_path.startswith("Vein/Content/Vein/"):
        model_path = model_path[len("Vein/Content/Vein") :]
    if model_path.startswith("Vein/"):
        model_path = model_path[len("Vein/") :]

    if _root is None:
        path = VEIN_PAK_DUMP_ROOT / model_path.lstrip("/")
    else:
        path = _root / model_path.lstrip("/")
    path = path.with_suffix(".json")
    return get_ue_model_by_path(path)


def get_type(ue_raw_model: list[dict]) -> Type[UEModel]:
    if len(ue_raw_model) == 0:
        raise VeinError("No content in supplied UE model.")
    model = ue_raw_model[0]
    if "Type" not in model:
        raise VeinError("UE model contains erroneous data.")
    model_type = model.get("Type", None)
    if model_type is None:
        raise VeinError("UE model contains no type.")
    ue_model = get_subclass_type(model_type)
    if ue_model is None:
        raise VeinError(
            "No UE model class to match [object_name=`'%s'%s'`, model_type='%s']",
            ue_raw_model[0]["Type"],
            ue_raw_model[0]["Name"],
            model_type,
        )
    return ue_model


async def prep_context_for_ue_model(node: Node, graph: Graph) -> dict:
    context: dict = {}
    context["model"] = node.ue_model
    context["infobox"] = await get_infobox(node=node, graph=graph)
    context["pre"] = await get_pre(node=node, graph=graph)
    context["obtaining"] = await get_obtaining(node=node, graph=graph)
    context["usage"] = await get_usages(node=node, graph=graph)
    context["categories"] = await get_categories(node=node, graph=graph)
    return context


async def get_pre(node: Node, graph: Graph) -> list[str]:
    model_info = node.ue_model.model_info
    pre = [
        f"'''{node.ue_model.display_name()}''' is a type of {model_info.super_type}."
    ]
    if sub := model_info.sub_type:
        pre.append(f"It's in the {sub} category.")
    return pre


async def get_infobox(node: Node, graph: Graph) -> Infobox | None:
    if node.ue_model.model_info.sub_type == "clothing":
        if not isinstance(node.ue_model, UEBlueprintGeneratedClass):
            raise ValueError("Invalid type during ClothingInfobox call")
        return ClothingInfobox(
            title=node.ue_model.display_name(),
            image=f"{node.ue_model.model_info.console_name}.png",
            description=str(node.ue_model.get_prop("description")),
            weight=get_wiki_weight_string(node.ue_model.get_prop("weight_lbs")),
            item_id=node.ue_model.model_info.console_name,
            run_speed_multiplier=node.ue_model.get_prop("run_speed_multiplier"),
            temperature_contribution=node.ue_model.get_prop("temperature_contribution"),
            water_resistance=node.ue_model.get_prop("water_resistance"),
            rain_resistance=node.ue_model.get_prop("rain_resistance"),
            radiation_resistance=node.ue_model.get_prop("radiation_resistance"),
            can_hotwire_with=node.ue_model.get_prop("can_hotwire_with"),
            blunt_resistance=node.ue_model.get_resistance("blunt"),
            bladed_resistance=node.ue_model.get_resistance("bladed"),
            bullet_resistance=node.ue_model.get_resistance("bullet"),
            zombie_bite_resistance=node.ue_model.get_resistance("zombie"),
            animal_bite_resistance=node.ue_model.get_resistance("animal"),
        )
    if node.ue_model.model_info.super_type == "fluid":
        return FluidInfobox(
            title=node.ue_model.display_name() or "",
            image=f"{node.ue_model.model_info.console_name}.png",
            smell_text=node.ue_model.get_prop("smell_text"),
            smell_rotten_text=node.ue_model.get_prop("smell_rotten_text"),
            decays=node.ue_model.get_prop("decays"),
            thirst_satisfaction_per_ml=node.ue_model.get_prop(
                "thirst_satisfaction_per_ml"
            ),
            density=node.ue_model.get_prop("density"),
            freezing_point=get_wiki_temperature_string(
                temp_f=node.ue_model.get_prop("freezing_point_f")
            ),
            sanitizes_wounds=node.ue_model.get_prop("sanitizes_wounds"),
            scent_strength=node.ue_model.get_prop("scent_strength"),
            scent_radius=node.ue_model.get_prop("scent_radius"),
            scent_radius_sqt=node.ue_model.get_prop("scent_radius_sqt"),
        )
    if node.ue_model.model_info.sub_type in ["melee", "firearm"]:
        bullet_info = get_bullet_info(node, graph)
        melee_damage: str | None = None
        melee_dps: str | None = None
        if node.ue_model.model_info.sub_type == "melee":
            mult = node.ue_model.get_prop("melee_damage_multiplier") or 1
            time = node.ue_model.get_prop("melee_time")
            if time is not None:
                md = BaseDamage.MELEE_WEAPON * mult
                melee_dps = str(round(md / time, 1))
                melee_damage = str(round(md, 1))
        return WeaponInfobox(
            title=node.ue_model.display_name() or "",
            image=f"{node.ue_model.model_info.console_name}.png",
            description=node.ue_model.get_prop("description"),
            weight=get_wiki_weight_string(node.ue_model.get_prop("weight_lbs")),
            item_id=node.ue_model.model_info.console_name,
            firearm_damage=bullet_info[1] if bullet_info else None,
            ammo_capacity=get_magazine_capacity_string(node),
            ammo_type=bullet_info[0] if bullet_info else None,
            melee_damage_type=get_damage_type(node=node, graph=graph),
            melee_swing_time=node.ue_model.get_prop("melee_time"),
            melee_base_damage=melee_damage,
            melee_base_dps=melee_dps,
            melee_tiredness=node.ue_model.get_prop("melee_tiredness"),
            used_as=get_tool_setup(node=node, graph=graph),
        )
    else:
        return ItemInfobox(
            title=node.ue_model.display_name(),
            image=f"{node.ue_model.model_info.console_name}.png",
            description=str(node.ue_model.get_prop("description")),
            weight=get_wiki_weight_string(node.ue_model.get_prop("weight_lbs")),
            item_id=node.ue_model.model_info.console_name,
            stackable=node.ue_model.get_prop("stackable"),
            stack_size=node.ue_model.get_prop("max_stack"),
            used_as=get_tool_setup(node=node, graph=graph),
        )


def get_tool_setup(node: Node, graph: Graph) -> str | None:
    tool_groups: list[WikiReference] = []
    if tool_setup := node.ue_model.get_prop("tool_setup"):
        for tool_ref in tool_setup.tools:
            if tool_node := graph.get_node(tool_ref.object_name, ue_model_type=UETool):
                tool_groups.append(
                    WikiReference(text=tool_node.ue_model.display_name())
                )
    if tool_groups:
        return ", ".join([str(t) for t in tool_groups])
    return None


def get_damage_type(node: Node, graph: Graph) -> str | None:
    damage_type = node.ue_model.get_prop("damage_type_class")
    if damage_type is None:
        return None
    damage_type_model = get_ue_model_by_reference(damage_type)
    if damage_type_model is None:
        return None
    damage_type_name = damage_type_model.get_prop("damage_type_name")
    if damage_type_name is None:
        return None
    return str(damage_type_name)


async def get_categories(node: Node, graph: Graph) -> set[str]:
    categories = node.ue_model.model_info.categories
    for linktype, n in node.edges:
        if linktype == LinkType.HAS_ITEM_TYPE:
            if isinstance(n.ue_model, UEItemType):
                categories.add(n.ue_model.display_name())
    if scent_strength := node.ue_model.get_prop("scent_strength"):
        if scent_strength != 0.0:
            categories.add("Scented")
    if node.ue_model.get_prop("fluid_type") is not None:
        categories.add("Fluid Container")
    return categories


def get_bullet_info(node: Node, graph: Graph) -> tuple[str, str] | None:
    magazines = get_related_models(node, LinkType.HAS_MAGAZINE)["edges"]
    if not magazines:
        return None
    magazine = magazines[0]
    ammo = magazine.ue_model.get_prop("bullet_type")
    if ammo is None:
        return None
    ammo_node = graph.get_node(
        key=ammo.object_name, ue_model_type=UEBlueprintGeneratedClass
    )
    if ammo_node is None:
        return None
    bullet_type = ammo_node.ue_model.get_prop("bullet_type")
    if bullet_type is None:
        return None
    bullet_type_node = graph.get_node(
        key=bullet_type.object_name, ue_model_type=UEBulletType
    )
    if bullet_type_node is None:
        return None
    return ammo_node.ue_model.display_name(), str(
        round(bullet_type_node.ue_model.properties.bullet_damage)
    )


def get_magazine_capacity_string(node: Node) -> str | None:
    magazines = get_related_models(node, LinkType.HAS_MAGAZINE)["edges"]
    magazine_strings = []
    for mag in magazines:
        capacity = mag.ue_model.get_prop("capacity")
        if capacity is None:
            if weapon_ammo_capacity := node.ue_model.get_prop("ammo_capacity"):
                magazine_strings.append(
                    f"[[{mag.ue_model.display_name().replace(' ', '_')}|{weapon_ammo_capacity} Rounds]]"
                )
            continue
        if capacity is not None:
            magazine_strings.append(
                f"[[{mag.ue_model.display_name().replace(' ', '_')}|{capacity} Rounds]]"
            )
    if not magazine_strings:
        if weapon_ammo_capacity := node.ue_model.get_prop("ammo_capacity"):
            return f"{weapon_ammo_capacity} Rounds"

    return "<br>".join(magazine_strings) if magazine_strings else None


def get_related_models(node: Node, linktype: LinkType) -> dict[str, list[Node]]:
    relations: dict[str, list[Node]] = {"edges": [], "neighbours": []}
    for linktype, n in node.edges:
        if linktype == linktype:
            relations["edges"].append(n)
    for linktype, n in node.neighbours:
        if linktype == linktype:
            relations["neighbours"].append(n)

    return relations


async def get_obtaining(node: Node, graph: Graph) -> dict[str, Any]:
    obtaining: dict[str, Any] = {}
    if node is None:
        return obtaining
    if node.ue_model is None:
        return obtaining

    if construction := await get_construction_info(node=node, graph=graph):
        obtaining["construction"] = construction
    if scavenging := await get_scavenging_info(node=node, graph=graph):
        obtaining["scavenging"] = scavenging

    return obtaining


async def get_usages(node: Node, graph: Graph) -> dict[str, Any]:
    usages: dict[str, Any] = {}
    if node is None:
        return usages
    if node.ue_model is None:
        return usages

    if dismantling_results := node.ue_model.get_prop("dismantling_results"):
        usages["dismantle_into"] = await get_dismantling_results(dismantling_results)
    if node.ue_model.get_prop("repair_ingredients") is not None:
        usages["repair"] = await get_repair_requirements(node=node)
    if (
        node.ue_model.get_prop("conditions_on_drink") is not None
        or node.ue_model.get_prop("conditions_on_inject") is not None
    ):
        usages["conditions"] = await get_conditions(ue_model=node.ue_model)
    if node.ue_model.get_prop("valid_batteries") is not None:
        usages["requirements"] = await get_tool_requirements(node=node, graph=graph)
    return usages


async def get_construction_info(node: Node, graph: Graph) -> Construction | None:
    result = Construction()
    if build_requirements := node.ue_model.get_prop("build_requirements"):
        for req in build_requirements:
            tool_model = get_ue_model_by_reference(req.item)
            result.build_requirements.append(
                ItemCountReference(text=tool_model.display_name(), count=req.quantity)
            )
    if tools := node.ue_model.get_prop("tool_object_requirements"):
        for tool in tools:
            tool_model = get_ue_model_by_reference(tool)
            result.tool_requirements.append(
                WikiReference(text=tool_model.display_name())
            )
    if stat_requirements := node.ue_model.get_prop("stat_requirements"):
        for stat in stat_requirements:
            if match := SKILL_PATTERN.match(stat.key):
                print("stat setting", stat.value)
                result.stat_requirements.append(
                    ItemCountReference(
                        text=match.group(1),
                        count=stat.value,
                    )
                )
    if maintenance_costs := node.ue_model.get_prop("maintenance_cost"):
        for cost in maintenance_costs:
            cost_model = get_ue_model_by_reference(cost.item)
            result.maintenance_costs.append(
                ItemCountReference(text=cost_model.display_name(), count=cost.quantity)
            )
    if result_xp := node.ue_model.get_prop("result_xp"):
        for xp in result_xp:
            if match := SKILL_PATTERN.match(xp.key):
                result.xp_rewards.append(
                    XPGainReference(
                        text=match.group(1),
                        amount=xp.value,
                    )
                )
    return result.validate()


async def get_scavenging_info(node: Node, graph: Graph) -> Scavenging | None:
    scavenging = Scavenging()
    # add what fluids a container can have when spawning
    if fluid_type := node.ue_model.get_prop("fluid_type"):
        fluid = graph.get_node(fluid_type.object_name, ue_model_type=UEFluidDefinition)
        if fluid is not None:
            scavenging.fluid_contents.append(
                FluidContent(
                    capacity=node.ue_model.get_prop("min_initial_amount"),
                    min=node.ue_model.get_prop("min_initial_amount"),
                    max=node.ue_model.get_prop("max_initial_amount"),
                    fluid_type=WikiReference(text=fluid.ue_model.display_name()),
                )
            )
    # show which containers a fluid can appear in
    if node.ue_model.model_info.template == "fluid":
        neighbours = get_related_models(node=node, linktype=LinkType.HAS_FLUID)[
            "neighbours"
        ]
        for neigh in neighbours:
            scavenging.fluids_contained.append(
                FluidContent(
                    container=WikiReference(text=neigh.ue_model.display_name()),
                    capacity=neigh.ue_model.get_prop("min_initial_amount"),
                    min=neigh.ue_model.get_prop("min_initial_amount"),
                    max=neigh.ue_model.get_prop("max_initial_amount"),
                    fluid_type=WikiReference(text=node.ue_model.display_name()),
                )
            )
    return scavenging if scavenging.is_valid() else None


async def get_dismantling_results(dismantling_results: UEReference) -> Dismantle | None:
    dismantle_model = get_ue_model_by_reference(model_reference=dismantling_results)
    if not isinstance(dismantle_model, UEItemSpawnlist):
        logger.warning(
            "Dismantling results model is not UEItemSpawnlist: %s",
            dismantling_results.object_name,
        )
        return None
    dismantle = Dismantle(
        min_count=dismantle_model.properties.item_count.min,
        max_count=dismantle_model.properties.item_count.max,
    )
    for item_list in dismantle_model.properties.lists:
        list_model = get_ue_model_by_reference(model_reference=item_list.list)
        if not isinstance(list_model, UEItemList):
            logger.warning(
                "Dismantling item list model is not UEItemList: %s",
                item_list.list.object_name,
            )
            continue
        dismantle_list = []
        for item in list_model.properties.items:
            item_model = get_ue_model_by_reference(model_reference=item.item)
            if not isinstance(item_model, UEBlueprintGeneratedClass):
                continue
            if item.item_count.max is None:
                logger.warning(
                    "Item in dismantling results has no max count: %s", item_model.name
                )
                continue

            dismantle_list.append(
                ItemMinMaxReference(
                    text=item_model.display_name(),
                    min=item.item_count.min,
                    max=item.item_count.max,
                )
            )
        dismantle.results.append(DismantleResult(items=dismantle_list))
    return dismantle if dismantle.is_valid() else None


async def get_repair_requirements(node: Node) -> Repair | None:
    if not isinstance(node.ue_model, UEBlueprintGeneratedClass):
        logger.warning(f"[Repair] Wrong type: {node.ue_model.get_object_name()}")
        return None
    repair_items: list[ItemCountReference] = []
    if repair_ingredients := node.ue_model.get_prop("repair_ingredients"):
        for ingredient in repair_ingredients:
            ingredient_model = get_ue_model_by_reference(ingredient.item)
            if not isinstance(ingredient_model, UEBlueprintGeneratedClass):
                continue
            repair_items.append(
                ItemCountReference(text=ingredient_model.display_name())
            )
    repair_tools: list[WikiReference] = []
    if repair_tool_objects := node.ue_model.get_prop("repair_tool_objects"):
        for tool in repair_tool_objects:
            tool_model = get_ue_model_by_reference(tool)
            if not isinstance(tool_model, UETool):
                continue
            repair_tools.append(WikiReference(text=str(tool_model.properties.name)))
    if len(repair_items) == 0:
        return None
    if len(repair_tools) == 0:
        repair_tools.append(WikiReference(text="Screwdriver"))
    return Repair(materials=repair_items, tools=repair_tools)


async def get_conditions(ue_model: UEModel) -> AllConditions:
    """Takes a Node which contains a UEModel which applies conditions when consumed."""

    all_conditions = AllConditions()
    if eat_ref := ue_model.get_prop("conditions_on_eat"):
        if fcs := get_food_condition_set(condition_ref=eat_ref):
            all_conditions.eat.append(fcs)
    if drink_ref := ue_model.get_prop("conditions_on_drink"):
        if fcs := get_food_condition_set(condition_ref=drink_ref):
            all_conditions.drink.append(fcs)
    if inject_ref := ue_model.get_prop("conditions_on_inject"):
        if fcs := get_food_condition_set(condition_ref=inject_ref):
            all_conditions.inject.append(fcs)
    return all_conditions


async def get_tool_requirements(node: Node, graph: Graph) -> Requirements | None:
    result = Requirements()
    if tool_setup := node.ue_model.get_prop("tool_setup"):
        if ammo_label := getattr(tool_setup, "tool_ammo_label", None):
            result.ammo_label = str(ammo_label)
        if default_ammo_ref := getattr(tool_setup, "default_ammo_item", None):
            default_ammo_model = get_ue_model_by_reference(default_ammo_ref)
            result.default_ammo = WikiReference(text=default_ammo_model.display_name())
        for ammo_ref in tool_setup.possible_ammo_attachments:
            ammo_model = get_ue_model_by_reference(ammo_ref)
            result.ammo.append(WikiReference(text=ammo_model.display_name()))
    if batteries := node.ue_model.get_prop("valid_batteries"):
        for battery_ref in batteries:
            battery_model = get_ue_model_by_reference(battery_ref)
            result.batteries.append(WikiReference(text=battery_model.display_name()))
    return result if result.is_valid() else None


def get_food_condition_set(condition_ref: UEReference) -> FoodConditionSet | None:
    """Takes a reference to a FCS and returns a parsed FoodConditionSet."""
    if condition_ue_model := get_ue_model_by_reference(condition_ref):
        return FoodConditionSet(
            conditions=extract_conditions(condition_ue_model),
            addiction=extract_addiction(condition_ue_model),
            xp_gain=extract_xp_gains(condition_ue_model),
            blood_sugar_impact=condition_ue_model.get_prop("blood_sugar_impact"),
        )
    return None


SKILL_PATTERN = re.compile(r".*ST_([^_]+)_C")


def extract_xp_gains(ue_model: UEModel) -> list[XPGainReference]:
    results = []
    if xp_gain := ue_model.get_prop("xp_gain"):
        for xp in xp_gain:
            if match := SKILL_PATTERN.match(xp.key):
                results.append(
                    XPGainReference(
                        text=match.group(1),
                        amount=xp.value,
                    )
                )
    return results


ADDICTION_PATTERN = re.compile(r".*ADD_([^_']+)'")


def extract_addiction(ue_model: UEModel) -> list[XPGainReference]:
    results = []
    if addictions := ue_model.get_prop("addiction_types_on_eat"):
        for addiction in addictions:
            if match := ADDICTION_PATTERN.match(addiction.key):
                results.append(
                    XPGainReference(
                        text=match.group(1),
                        amount=addiction.value,
                    )
                )
    return results


CONDITION_PATTERN = re.compile(r".*C_([^_]+)_C")


def extract_conditions(ue_model: UEModel) -> list[ConditionReference]:
    """Extract a set of conditions from a FCS model"""
    results = []
    if conditions := ue_model.get_prop("conditions_on_eat"):
        for condition in conditions:
            if match := CONDITION_PATTERN.match(condition.key):
                results.append(
                    ConditionReference(
                        text=match.group(1),
                        value=condition.value,
                    )
                )
    return results
