from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Iterable, Type, TypeVar

from pydantic import BaseModel, ConfigDict, Field

logger = logging.getLogger(__name__)

VEIN_PAK_DUMP_ROOT = Path("/mnt/c/Users/havard/Downloads/Vein")
N = TypeVar("N", bound="UEModel")


@dataclass
class UEModelInfo:
    template: str | None = None
    sub_type: str | None = None
    super_type: str | None = None
    console_name: str | None = None
    categories: set[str] = field(default_factory=set)


class UEFlags(Enum):
    RF_Public = 0x00000001
    RF_Transactional = 0x00000008
    RF_WasLoaded = 0x00000040
    RF_LoadCompleted = 0x00000200


class UEBaseModel(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
        use_enum_values=True,
        populate_by_name=True,
    )


class UEBasePropertyModel(UEBaseModel):
    name: dict[str, str] = Field(default_factory=dict, alias="Name")
    description: dict[str, str] = Field(default_factory=dict, alias="Description")
    stackable: bool = Field(default=False, alias="Stackable")
    weight_lbs: float | None = Field(default=None, alias="Weight")
    dismantling_results: dict[str, str] = Field(default_factory=dict, alias="DismantlingResults")
    item_type: dict[str, str] = Field(..., alias="Type")

    def s_name(self) -> str:
        return self.name.get("SourceString", "Error")

    def s_description(self) -> str:
        return self.description.get("SourceString", "Error")

    def s_dismantling_results(self) -> str:
        return self.dismantling_results.get("SourceString", "Error")

    def s_item_type(self) -> str:
        return self.item_type.get("ObjectName", "Error")


class UEModel(UEBaseModel):
    # UE fields
    type: str = Field(..., alias="Type")
    name: str = Field(..., alias="Name")
    super_struct: UEReference | None = Field(default=None, alias="SuperStruct")
    # custom fields
    _model_info: UEModelInfo = UEModelInfo()

    @property
    def model_info(self) -> UEModelInfo:
        if ton := self.get_type_object_name():
            if match := re.match(r"(Item)Type'IT_(\w+)'", ton):
                self._model_info.super_type = match.group(1).lower()
                self._model_info.sub_type = match.group(2).lower()
                self._model_info.template = self._model_info.super_type
        elif self.super_struct is not None:
            if match := re.match(r"Class'(.*)(Item)'", self.super_struct.object_name):
                if item_type := match.group(1):
                    self._model_info.sub_type = item_type.lower()
                elif cn := self._model_info.console_name:
                    if "melee" in cn.lower():
                        self._model_info.sub_type = "melee"
                elif self.get_prop("melee_time") is not None:
                    self._model_info.sub_type = "melee"
                self._model_info.super_type = match.group(2).lower()
                self._model_info.template = match.group(2).lower()
        return self._model_info

    def get_object_name(self) -> str:
        return f"{self.type}'{self.name}'"

    def get_type_object_name(self) -> str:
        if obj := getattr(self, "object", None):
            if props := getattr(obj, "properties", None):
                if _type := getattr(props, "type", None):
                    return _type.object_name
        return ""

    def display_name(self) -> str:
        if obj := getattr(self, "object", None):
            if props := getattr(obj, "properties", None):
                if name := getattr(props, "name", None):
                    return str(name).strip()
        if props := getattr(self, "properties", None):
            if name := getattr(props, "name", None):
                return str(name).strip()
            if label := getattr(props, "label", None):
                return str(label).strip()
        if match := re.match(r".*?_([^_]+)(_C)?", self.name):
            return "".join(" " + c if c.isupper() else c for c in match.group(1)).strip()
        raise ValueError(f"Unable to produce a display name for {self.get_object_name()}")

    def get_prop(self, prop_name: str) -> Any:
        if obj := getattr(self, "object", None):
            if props := getattr(obj, "properties", None):
                return getattr(props, prop_name, None)
        if props := getattr(self, "properties", None):
            return getattr(props, prop_name, None)
        return None

    @classmethod
    def get_subclasses(cls) -> Iterable[Type[UEModel]]:
        for subclass in cls.__subclasses__():
            yield from subclass.get_subclasses()
            yield subclass


class UEColor(UEBaseModel):
    r: float = Field(..., serialization_alias="R", validation_alias="R")
    g: float = Field(..., serialization_alias="G", validation_alias="G")
    b: float = Field(..., serialization_alias="B", validation_alias="B")
    a: float = Field(..., serialization_alias="A", validation_alias="A")
    hex: str = Field(..., serialization_alias="Hex", validation_alias="Hex")


class UEReference(UEBaseModel):
    object_name: str = Field(..., alias="ObjectName")
    object_path: str = Field(..., alias="ObjectPath")

    def __hash__(self) -> int:
        return self.object_name.__hash__()

    async def get_model(self) -> "UEModel":
        from vein_wiki_tools.clients.pakdump.services import get_ue_model_by_reference

        return get_ue_model_by_reference(self, _type=UEModel)


class UEStrKeyFloatValuePair(UEBaseModel):
    key: str = Field(..., alias="Key")
    value: float = Field(..., alias="Value")


class UEItemTypeProperties(UEBaseModel):
    name: UELocalizedString | UECultureInvariantString | None = Field(default=None, alias="Name")
    icon: UEReference = Field(..., alias="Icon")
    color: UEColor = Field(..., alias="Color")
    order: int | None = Field(default=None)


class UEToolSetup(UEBaseModel):
    tools: list[UEReference] = Field(default_factory=list, alias="Tools")
    has_ammo: bool | None = Field(default=None, alias="bHasAmmo")
    default_ammo_item: UEReference | None = Field(default=None, alias="DefaultAmmoItem")
    tool_ammo_label: UELocalizedString | UECultureInvariantString | None = Field(default=None, alias="ToolAmmoLabel")
    possible_ammo_attachments: list[UEReference] = Field(default_factory=list, alias="PossibleAmmoItems")


class UEItemType(UEModel):
    properties: UEItemTypeProperties = Field(..., alias="Properties")

    def display_name(self) -> str:
        return str(self.properties.name)


class UELocalizedString(UEBaseModel):
    namespace: str | None = Field(default=None, alias="Namespace")
    table_id: str | None = Field(default=None, alias="TableId")
    key: str = Field(..., alias="Key")
    source_string: str = Field(..., alias="SourceString")
    localized_string: str = Field(..., alias="LocalizedString")

    def __str__(self) -> str:
        return self.source_string


class UECultureInvariantString(UEBaseModel):
    culture_invariant_string: str = Field(..., alias="CultureInvariantString")

    def __str__(self) -> str:
        return self.culture_invariant_string


class UEQuantityModel(UEBaseModel):
    item: UEReference = Field(..., alias="Item")
    quantity: int = Field(..., alias="Quantity")


class UEBGCProperties(UEBaseModel):
    # common
    type: UEReference | None = Field(default=None, alias="Type")
    name: UELocalizedString | UECultureInvariantString | None = Field(default=None, alias="Name")
    short_name: UELocalizedString | UECultureInvariantString | None = Field(default=None, alias="ShortName")
    damage_type_name: UELocalizedString | UECultureInvariantString | None = Field(default=None, alias="DamageTypeName")
    description: UELocalizedString | UECultureInvariantString | None = Field(default=None, alias="Description")
    item_type: UEReference | None = Field(default=None, alias="Type")
    stackable: bool = Field(default=False, alias="bStackable")
    max_stack: int | None = Field(default=None, alias="MaxStack")
    damageable: bool | None = Field(default=None, alias="Damageable")
    weight_lbs: float | None = Field(default=None, alias="Weight")
    dismantling_results: UEReference | None = Field(default=None, alias="DismantlingResults")
    min_damage_per_use: float | None = Field(default=None, alias="MinDamagePerUse")
    max_damage_per_use: float | None = Field(default=None, alias="MaxDamagePerUse")
    repair_ingredients: list[UEQuantityModel] = Field(default_factory=list, alias="RepairIngredients")
    repair_tool_objects: list[UEReference] = Field(default_factory=list, alias="RepairToolObjects")
    tags: list[UEReference] = Field(default_factory=list, alias="Tags")
    valid_batteries: list[UEReference] = Field(default_factory=list, alias="ValidBatteries")
    # melee
    melee_damage_multiplier: float | None = Field(default=None, alias="MeleeDamageMultiplier")
    melee_time: float | None = Field(default=None, alias="MeleeTime")
    melee_tiredness: float | None = Field(default=None, alias="MeleeTiredness")
    damage_type_class: UEReference | None = Field(default=None, alias="DamageTypeClass")
    # firearm
    ammo_capacity: int | None = Field(default=None, alias="AmmoCapacity")
    ammo_classes: list[UEReference] = Field(default_factory=list, alias="AmmoClasses")
    magazine_items: list[UEReference] = Field(default_factory=list, alias="MagazineItems")
    rounds_per_minute: float | None = Field(default=None, alias="RPM")
    reload_duration_secs: float | None = Field(default=None, alias="ReloadDuration")
    # ammo / magazine
    capacity: float | int | None = Field(default=None, alias="Capacity")
    bullet_type: UEReference | None = Field(default=None, alias="BulletType")
    # food / fluids
    base_hunger_satisfaction: float | None = Field(default=None, alias="BaseHungerSatisfaction")
    thirst_addition: float | None = Field(default=None, alias="ThirstAddition")
    base_thirst_addition: float | None = Field(default=None, alias="BaseThirstAddition")
    conditions_on_eat: UEReference | None = Field(default=None, alias="ConditionsOnEat")
    cooling_speed: float | None = Field(default=None, alias="CoolingSpeed")
    fluid_type: UEReference | None = Field(default=None, alias="FluidType")
    min_initial_amount: float | None = Field(default=None, alias="MinInitialAmount")
    max_initial_amount: float | None = Field(default=None, alias="MaxInitialAmount")
    # clothing
    temperature_contribution: float | None = Field(default=None, alias="TemperatureContribution")
    run_speed_multiplier: float | None = Field(default=None, alias="RunSpeedMultiplier")
    can_hotwire_with: bool | None = Field(default=None, alias="bCanHotwireWith")
    # Armor ratings are the amount of blocked HP
    armor_ratings: list[UEStrKeyFloatValuePair] | None = Field(default=None, alias="ArmorRatings")
    # Resistances are a multiplier showing the percent coming through
    water_resistance: float | None = Field(default=None, alias="WaterResistance")
    rain_resistance: float | None = Field(default=None, alias="RainResistance")
    radiation_resistance: float | None = Field(default=None, alias="RadiationResistance")
    # Tools
    tool_setup: UEToolSetup | None = Field(default=None, alias="ToolSetup")


class UEBlueprintGeneratedClassObject(UEBaseModel):
    type: str = Field(..., alias="Type")
    name: str = Field(..., alias="Name")
    template: UEReference | None = Field(default=None, alias="Template")
    properties: UEBGCProperties = Field(..., alias="Properties")

    @property
    def clean_type(self) -> str:
        if not self.type.endswith("_C"):
            logger.warning("Type name does not end with _C: %s", self.type)
        return self.type[:-2]


class UEBlueprintGeneratedClass(UEModel):
    super_struct: UEReference | None = Field(default=None, alias="SuperStruct")
    object: UEBlueprintGeneratedClassObject | None = Field(default=None)

    def get_name(self) -> str:
        if self.object is not None:
            return self.object.name
        return self.name

    def get_object_name(self) -> str:
        return f"{self.type}'{self.name}'"

    def get_default_object_name(self) -> str | None:
        if self.object is None:
            return None
        return f"{self.object.type}'{self.object.name}'"

    def get_prop_object_name(self, prop_name: str) -> str | None:
        if self.object is not None:
            prop = getattr(self.object.properties, prop_name, None)
            if isinstance(prop, UEReference):
                return prop.object_name
        return None

    def get_resistance(self, name: str) -> float | None:
        if obj := getattr(self, "object", None):
            if props := getattr(obj, "properties", None):
                if armor_ratings := getattr(props, "armor_ratings", None):
                    for r in armor_ratings:
                        if name in r.key.lower():
                            return r.value
        return None

    def __repr__(self) -> str:
        return f"UEModel(interface={self.type}'{self.name}', object={self.get_name()})"
