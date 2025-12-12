import json
from functools import cache
from pathlib import Path
from typing import Type

from vein_wiki_tools.clients.pakdump import get_subclass_type
from vein_wiki_tools.clients.pakdump.ammo import UEBulletType
from vein_wiki_tools.clients.pakdump.models import UEBlueprintGeneratedClass, UEModel, UEReference
from vein_wiki_tools.clients.pakdump.spawnlists import UEItemList, UEItemSpawnlist
from vein_wiki_tools.data.models import Graph, Node
from vein_wiki_tools.errors import VeinError
from vein_wiki_tools.models.common import Dismantle, DismantleResult, Infobox, ItemInfobox, ItemMinMaxReference, LinkType, WeaponInfobox
from vein_wiki_tools.utils.file_helper import get_vein_root
from vein_wiki_tools.utils.logging import getLogger
from vein_wiki_tools.utils.metrology import imperial_to_metric

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
                    raise ValueError(f"Template reference can't be handled in file: {path}")
                template_model = get_ue_model_by_reference(template)
                if not isinstance(template_model, UEBlueprintGeneratedClass):
                    raise ValueError(f"Template model is not a UEModel in file: {path}")
                if template_model.object is None:
                    raise ValueError(f"Template model has no object in file: {path}")
                temp_props = template_model.object.properties.model_dump(exclude_none=True, exclude_unset=True)
                temp_props.update(obj.get("Properties", {}))
                obj["Properties"] = temp_props
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
        raise VeinError("No UE model class to match %s", model_type)
    return ue_model


async def prep_context_for_ue_model(node: Node, graph: Graph) -> dict:
    context: dict = {}
    context["model"] = node.ue_model
    context["infobox"] = await get_infobox(node=node, graph=graph)
    context["obtaining"] = await get_obtaining(node=node, graph=graph)
    context["usage"] = await get_usages(node=node, graph=graph)
    context["categories"] = await get_categories(node=node, graph=graph)

    return context


async def get_infobox(node: Node, graph: Graph) -> Infobox | None:
    if node.ue_model.template == "firearm":
        bullet_info = get_bullet_info(node, graph)
        return WeaponInfobox(
            title=node.ue_model.display_name() or "",
            image=f"{node.ue_model.console_name}.png",
            description=str(node.ue_model.get_prop("description")),
            weight=get_wiki_weight_string(node.ue_model),
            item_id=node.ue_model.console_name,
            firearm_damage=bullet_info[1] if bullet_info else None,
            ammo_capacity=get_magazine_capacity_string(node),
            ammo_type=bullet_info[0] if bullet_info else None,
        )
    else:
        return ItemInfobox(
            title=node.ue_model.display_name(),
            image=f"{node.ue_model.console_name}.png",
            description=str(node.ue_model.get_prop("description")),
            weight=get_wiki_weight_string(node.ue_model),
            item_id=node.ue_model.console_name,
            stackable=node.ue_model.get_prop("stackable"),
            stack_size=node.ue_model.get_prop("max_stack"),
        )


async def get_categories(node: Node, graph: Graph) -> list[str]:
    categories: list[str] = []
    for linktype, node in node.edges:
        if linktype == LinkType.HAS_ITEM_TYPE:
            if isinstance(node.ue_model, UEItemType):
                itemtype = get_type(node.ue_model)
                if itemtype:
                    categories.append(itemtype)
    return categories


async def get_obtaining(node: Node, graph: Graph) -> str | None:
    # Placeholder for obtaining logic
    return None


def get_wiki_weight_string(ue_model: UEModel) -> str | None:
    weight_lbs = ue_model.get_prop("weight_lbs")
    if weight_lbs is None:
        return None
    return f"{weight_lbs:.2f} lbs / {imperial_to_metric(pounds=weight_lbs):.2f} kg"


def get_bullet_info(node: Node, graph: Graph) -> tuple[str, str] | None:
    magazines = get_related_models(node, LinkType.HAS_MAGAZINE)["edges"]
    if not magazines:
        return None
    magazine = magazines[0]
    ammo = magazine.ue_model.get_prop("bullet_type").object_name
    if ammo is None:
        return None
    ammo_node = graph.get_node(key=ammo, ue_model_type=UEBlueprintGeneratedClass)
    if ammo_node is None:
        return None
    bullet_type = ammo_node.ue_model.get_prop("bullet_type").object_name
    if bullet_type is None:
        return None
    bullet_type_node = graph.get_node(key=bullet_type, ue_model_type=UEBulletType)
    if bullet_type_node is None:
        return None
    return ammo_node.ue_model.display_name(), str(round(bullet_type_node.ue_model.properties.bullet_damage))


def get_magazine_capacity_string(node: Node) -> str | None:
    magazines = get_related_models(node, LinkType.HAS_MAGAZINE)["edges"]
    magazine_strings = []
    for mag in magazines:
        capacity = mag.ue_model.get_prop("capacity")
        if capacity is None:
            if weapon_ammo_capacity := node.ue_model.get_prop("ammo_capacity"):
                magazine_strings.append(f"[[{mag.ue_model.display_name().replace(' ', '_')}|{weapon_ammo_capacity} Rounds]]")
            continue
        if capacity is not None:
            magazine_strings.append(f"[[{mag.ue_model.display_name().replace(" ", "_")}|{capacity} Rounds]]")
    if not magazine_strings:
        if weapon_ammo_capacity := node.ue_model.get_prop("ammo_capacity"):
            return f"{weapon_ammo_capacity} Rounds"

    return "<br>".join(magazine_strings) if magazine_strings else None


def get_related_models(node: Node, relation: LinkType) -> dict[str, list[Node]]:
    relations: dict[str, list[Node]] = {"edges": [], "neighbours": []}
    for linktype, n in node.edges:
        if linktype == relation:
            relations["edges"].append(n)
    for linktype, n in node.neighbours:
        if linktype == relation:
            relations["neighbours"].append(n)

    return relations


async def get_usages(node: Node, graph: Graph) -> dict[str, str]:
    usages = {}
    if node is None:
        return usages
    if node.ue_model is None:
        return usages

    if dismantling_results := node.ue_model.get_prop("dismantling_results"):
        usages["dismantle_into"] = await get_dismantling_results(dismantling_results)
    if repair_ingredients := node.ue_model.get_prop("repair_ingredients"):
        usages["repair_ingredients"] = repair_ingredients

    return usages


async def get_dismantling_results(dismantling_results: UEReference) -> Dismantle | None:
    dismantle_model = get_ue_model_by_reference(model_reference=dismantling_results)
    if not isinstance(dismantle_model, UEItemSpawnlist):
        logger.warning("Dismantling results model is not UEItemSpawnlist: %s", dismantling_results.object_name)
        return None
    dismantle = Dismantle(
        min_count=dismantle_model.properties.item_count.min,
        max_count=dismantle_model.properties.item_count.max,
    )
    for item_list in dismantle_model.properties.lists:
        list_model = get_ue_model_by_reference(model_reference=item_list.list)
        if not isinstance(list_model, UEItemList):
            logger.warning("Dismantling item list model is not UEItemList: %s", item_list.list.object_name)
            continue
        dismantle_list = []
        for item in list_model.properties.items:
            item_model = get_ue_model_by_reference(model_reference=item.item)
            if not isinstance(item_model, UEBlueprintGeneratedClass):
                continue
            if item.item_count.max is None:
                logger.warning("Item in dismantling results has no max count: %s", item_model.name)
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
