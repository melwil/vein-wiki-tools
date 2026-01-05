from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import Iterable, Type

from pydantic import ConfigDict, Field

from vein_wiki_tools.base import RootSchema
from vein_wiki_tools.utils.metrology import imperial_to_metric, metric_to_imperial


class NodeContent(RootSchema):
    model_config = ConfigDict(
        extra="ignore",
        use_enum_values=True,
    )

    @classmethod
    def get_subclasses(cls) -> Iterable[Type[NodeContent]]:
        for subclass in cls.__subclasses__():
            yield from subclass.get_subclasses()
            yield subclass


class BaseDamage(IntEnum):
    FIST = 7
    SHOVE = 5
    MELEE_WEAPON = 20


class LinkType(Enum):
    HAS_BULLET_TYPE = "HAS_BULLETTYPE"
    HAS_ITEM_TYPE = "HAS_ITEMTYPE"
    HAS_AMMO = "HAS_AMMO"
    HAS_MAGAZINE = "HAS_MAGAZINE"
    HAS_FLUID = "HAS_FLUID"
    HAS_CRAFTING_RECIPE = "HAS_CRAFTING_RECIPE"
    HAS_COOKING_RECIPE = "HAS_COOKING_RECIPE"
    HAS_SCHEMATIC = "HAS_SCHEMATIC"
    HAS_DISMANTLE_RESULT = "HAS_DISMANTLE_RESULT"
    HAS_TOOL_GROUP = "HAS_TOOL_GROUP"


class Link(RootSchema):
    from_node_id: str = Field(..., serialization_alias="FromNodeID")
    to_node_id: str = Field(..., serialization_alias="ToNodeID")
    link_type: LinkType = Field(..., serialization_alias="LinkType")


class Category(NodeContent):
    name: str = Field(..., serialization_alias="Name")
    sync_to_wiki: bool = Field(..., serialization_alias="SyncToWiki")


@dataclass
class Infobox:
    infobox_template: str = ""
    title: str | None = None
    image: str | None = None
    description: str | None = None
    weight: str | None = None
    item_id: str | None = None


@dataclass
class ClothingInfobox(Infobox):
    infobox_template: str = "infoboxes/infobox_clothing.jinja"
    run_speed_multiplier: float | None = None
    temperature_contribution: float | None = None
    water_resistance: float | None = None
    rain_resistance: float | None = None
    radiation_resistance: float | None = None
    can_hotwire_with: float | None = None
    blunt_resistance: float | None = None
    bladed_resistance: float | None = None
    bullet_resistance: float | None = None
    zombie_bite_resistance: float | None = None
    animal_bite_resistance: float | None = None


@dataclass
class FluidInfobox(Infobox):
    infobox_template: str = "infoboxes/infobox_fluid.jinja"
    smell_text: str | None = None
    smell_rotten_text: str | None = None
    decays: bool = False
    thirst_satisfaction_per_ml: float | None = None
    density: float | str | None = None
    freezing_point: str | None = None
    wash_target: float | str | None = None
    detergent_multiplier: float | str | None = None
    sanitizes_wounds: bool = False
    scent_strength: float | None = None
    scent_radius: float | None = None
    scent_radius_sqt: float | None = None


@dataclass
class ItemInfobox(Infobox):
    infobox_template: str = "infoboxes/infobox_item.jinja"
    stackable: bool = False
    stack_size: int | None = None
    renewable: bool | None = None
    used_as: str | None = None

    def stackable_str(self) -> str:
        if not self.stackable:
            return "No"
        return f"Yes ({self.stack_size if self.stack_size else 50})"

    def renewable_str(self) -> str:
        return ""


@dataclass
class WeaponInfobox(Infobox):
    infobox_template: str = "infoboxes/infobox_weapon.jinja"
    firearm_damage: str | None = None
    ammo_capacity: str | None = None
    ammo_type: str | None = None
    melee_damage_type: str | None = None
    melee_swing_time: str | None = None
    melee_base_damage: str | None = None
    melee_base_dps: str | None = None
    melee_tiredness: str | None = None
    used_as: str | None = None


@dataclass
class WikiReference:
    link: str | None = None
    text: str | None = None

    def __str__(self) -> str:
        if self.link and self.text:
            return f"[[{self.link.replace(' ', '_')}|{self.text}]]"
        elif self.link:
            return f"[[{self.link.replace(' ', '_')}]]"
        elif self.text:
            return f"[[{self.text}]]"
        else:
            raise ValueError("WikiReference must have at least a link or text")


@dataclass
class ItemCountReference(WikiReference):
    count: int | str = 1

    def __str__(self) -> str:
        base = super().__str__()
        return f"{self.count}× {base}"


@dataclass
class ItemMinMaxReference(WikiReference):
    min: int | str = 0
    max: int | str = 0

    def __str__(self) -> str:
        base = super().__str__()
        return f"{self.min}-{self.max}× {base}"


@dataclass
class SkillReference(WikiReference):
    level: float = 0

    def __str__(self) -> str:
        base = super().__str__()
        if self.level == 0:
            return f"No {base}"
        return f"{self.level} {base}"


@dataclass
class XPGainReference(WikiReference):
    amount: float = 0

    def __str__(self) -> str:
        base = super().__str__()
        if self.amount == 0:
            return f"No {base}"
        return f"{self.amount} {base}"


@dataclass
class DismantleResult:
    items: list[ItemMinMaxReference]


@dataclass
class Dismantle:
    tools: list[WikiReference]
    min: int
    max: int
    results: list[DismantleResult]

    def __init__(
        self,
        tools: list[WikiReference] | None = None,
        min_count: int | None = None,
        max_count: int | None = None,
        results: list[DismantleResult] | None = None,
    ) -> None:
        self.tools = tools or []
        self.min = min_count or 0
        self.max = max_count or min_count or 0
        self.results = results or []

    def is_valid(self) -> bool:
        return len(self.results) > 0 and self.min >= 0

    def tools_str(self) -> str:
        if not self.tools:
            return "No tool required"
        return "<br>".join(str(tool) for tool in self.tools)

    def rolls_str(self) -> str:
        if self.min == 0 and self.max == 0:
            return "No rolls"
        if self.min == self.max:
            return str(self.min)
        return f"{self.min} - {self.max}"

    def results_str(self) -> str:
        result_lines = []
        for result in self.results:
            item_set = []
            for item in result.items:
                item_set.append(str(item))
            result_lines.append("<br>".join(item_set))
        return "<br><br>".join(result_lines)


@dataclass
class Repair:
    materials: list[ItemCountReference]
    tools: list[WikiReference] | None = None

    def tools_str(self) -> str:
        if not self.tools:
            return "No tool required"
        return "<br>".join(str(tool) for tool in self.tools)

    def materials_str(self) -> str:
        material_lines = []
        for material in self.materials:
            material_lines.append(str(material))
        return "<br>".join(material_lines)


@dataclass
class FluidCapacity:
    capacity: float

    def capacity_str(self):
        return get_wiki_fluid_capacity_string(self.capacity)


@dataclass
class FluidContent(FluidCapacity):
    min: float
    max: float
    fluid_type: WikiReference
    container: WikiReference | None

    def __init__(
        self,
        capacity: float,
        min: float,
        fluid_type: WikiReference,
        max: float | None = None,
        container: WikiReference | None = None,
    ):
        if max is None:
            max = capacity
        self.capacity = capacity
        self.min = min
        self.max = max
        self.fluid_type = fluid_type
        self.container = container

    def content_str(self):
        return f"{self.capacity_str()} {self.fluid_type}"

    def content_span_str(self):
        return get_wiki_fluid_span_string(self.min, self.max)


def get_wiki_weight_string(pounds: float | None) -> str:
    if pounds is None:
        return ""
    return f"{pounds:.2f} lbs / {imperial_to_metric(pounds=pounds):.2f} kg"


def get_wiki_fluid_capacity_string(fluid_ml: float) -> str:
    imperial_capacity = metric_to_imperial(ml=fluid_ml)
    if imperial_capacity is None:
        imperial_capacity = 0
    metric_unit = "mL"
    if fluid_ml > 1000:
        fluid_ml /= 1000
        metric_unit = "L"
    return f"{imperial_capacity:.3f} fl. oz. / {fluid_ml:.1f} {metric_unit}"


def get_wiki_fluid_span_string(fluid_ml_min: float, fluid_ml_max: float) -> str:
    imperial_capacity_min = metric_to_imperial(ml=fluid_ml_min)
    imperial_capacity_max = metric_to_imperial(ml=fluid_ml_max)
    metric_unit = "mL"
    if fluid_ml_max > 1000:
        fluid_ml_min /= 1000
        fluid_ml_max /= 1000
        metric_unit = "L"
    if fluid_ml_min == fluid_ml_max:
        return f"{imperial_capacity_max:.3f} fl. oz.<br>{fluid_ml_max:.1f} {metric_unit}"
    return f"{imperial_capacity_min:.3f}-{imperial_capacity_max:.3f} fl. oz.<br>{fluid_ml_min:.1f}-{fluid_ml_max:.1f} {metric_unit}"


def get_wiki_temperature_string(temp_f: float | None) -> str:
    if temp_f is None:
        return ""
    c = imperial_to_metric(fahrenheit=temp_f)
    return f"{temp_f}°F / {c}°C"


@dataclass
class Scavenging:
    fluid_contents: list[FluidContent] = field(default_factory=list)
    fluids_contained: list[FluidContent] = field(default_factory=list)

    def is_valid(self):
        if self.fluid_contents or self.fluids_contained:
            return True
        return False


@dataclass
class ConditionReference(WikiReference):
    value: float = 0.0

    def __str__(self) -> str:
        base = super().__str__()
        if self.value == 0.0:
            return f"No {base}"
        return f"{self.value} {base}"


@dataclass
class FoodConditionSet:
    addiction: list[XPGainReference] = field(default_factory=list)
    blood_sugar_impact: float | None = None
    conditions: list[ConditionReference] = field(default_factory=list)
    xp_gain: list[XPGainReference] = field(default_factory=list)


@dataclass
class AllConditions:
    eat: list[FoodConditionSet] = field(default_factory=list)
    drink: list[FoodConditionSet] = field(default_factory=list)
    inject: list[FoodConditionSet] = field(default_factory=list)


@dataclass
class Requirements:
    ammo: list[WikiReference] = field(default_factory=list)
    default_ammo: WikiReference | None = field(default=None)
    ammo_label: str | None = field(default=None)
    batteries: list[WikiReference] = field(default_factory=list)

    def is_valid(self) -> bool:
        return len(self.ammo) > 0 or len(self.batteries) > 0


@dataclass
class Construction:
    build_requirements: list[ItemCountReference] = field(default_factory=list)
    tool_requirements: list[WikiReference] = field(default_factory=list)
    maintenance_costs: list[ItemCountReference] = field(default_factory=list)
    stat_requirements: list[ItemCountReference] = field(default_factory=list)
    xp_rewards: list[XPGainReference] = field(default_factory=list)

    def tools_str(self) -> str:
        if len(self.tool_requirements) == 0:
            return "No tools required"
        return "<br>".join(str(t) for t in self.tool_requirements)

    def maintenance_str(self) -> str:
        if len(self.maintenance_costs) == 0:
            return "No maintenance cost"
        return "<br>".join(str(m) for m in self.maintenance_costs)

    def build_requirements_str(self) -> str:
        if len(self.build_requirements) == 0:
            return "No materials required"
        return "<br>".join(str(r) for r in self.build_requirements)

    def stat_requirements_str(self) -> str:
        if len(self.stat_requirements) == 0:
            return "No stats required"
        return "<br>".join(str(s) for s in self.stat_requirements)

    def validate(self) -> Construction | None:
        return self if len(self.build_requirements) > 0 else None
