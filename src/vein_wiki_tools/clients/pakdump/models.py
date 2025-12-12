from __future__ import annotations

import logging
from enum import Enum
from pathlib import Path
from typing import Any, Iterable, Type, TypeVar

from pydantic import BaseModel, ConfigDict, Field

logger = logging.getLogger(__name__)

VEIN_PAK_DUMP_ROOT = Path("/mnt/c/Users/havard/Downloads/Vein")
N = TypeVar("N", bound="UEModel")


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
    type: str = Field(..., alias="Type")
    name: str = Field(..., alias="Name")
    template: str | None = Field(default=None)
    console_name: str | None = Field(default=None)

    @property
    def clean_type(self) -> str:
        if not self.type.endswith("_C"):
            logger.warning("Type name does not end with _C: %s", self.type)
        return self.type[:-2]

    def get_object_name(self) -> str:
        return f"{self.type}'{self.name}'"

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


class UEFluid(UEModel):
    pass


class UEItemType(UEModel):
    pass


class UELocalizedString(UEBaseModel):
    namespace: str = Field(..., alias="Namespace")
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
    description: UELocalizedString | UECultureInvariantString | None = Field(default=None, alias="Description")
    item_type: UEReference | None = Field(default=None, alias="Type")
    stackable: bool = Field(default=False, alias="bStackable")
    max_stack: int | None = Field(default=None, alias="MaxStack")
    damageable: bool | None = Field(default=None, alias="Damageable")
    weight_lbs: float | None = Field(default=None, alias="Weight")
    dismantling_results: UEReference | None = Field(default=None, alias="DismantlingResults")
    repair_ingredients: list[UEQuantityModel] = Field(default_factory=list, alias="RepairIngredients")
    repair_tool_objects: list[UEReference] = Field(default_factory=list, alias="RepairToolObjects")
    tags: list[UEReference] = Field(default_factory=list, alias="Tags")
    # firearm
    ammo_capacity: int | None = Field(default=None, alias="AmmoCapacity")
    ammo_classes: list[UEReference] = Field(default_factory=list, alias="AmmoClasses")
    magazine_items: list[UEReference] = Field(default_factory=list, alias="MagazineItems")
    rounds_per_minute: float | None = Field(default=None, alias="RPM")
    reload_duration_secs: float | None = Field(default=None, alias="ReloadDuration")
    # ammo / magazine
    capacity: int | None = Field(default=None, alias="Capacity")
    bullet_type: UEReference | None = Field(default=None, alias="BulletType")
    # food
    base_hunger_satisfaction: float | None = Field(default=None, alias="BaseHungerSatisfaction")
    thirst_addition: float | None = Field(default=None, alias="ThirstAddition")
    base_thirst_addition: float | None = Field(default=None, alias="BaseThirstAddition")
    conditions_on_eat: UEReference | None = Field(default=None, alias="ConditionsOnEat")


class UEInterface(UEBaseModel):
    type: str = Field(..., alias="Type")
    name: str = Field(..., alias="Name")
    properties: UEBGCProperties | None = Field(default=None, alias="Properties")


class UEBGCObject(UEBaseModel):
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
    object: UEBGCObject | None = Field(default=None, alias="objects")

    def display_name(self) -> str:
        if self.object is not None:
            return str(self.object.properties.name)
        return str(self.name)

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

    def get_type_object_name(self) -> str:
        if self.object is not None:
            if self.object.properties.type is not None:
                return self.object.properties.type.object_name
        return f"{self.type}'{self.name}'"

    def get_prop_object_name(self, prop_name: str) -> str | None:
        if self.object is not None:
            prop = getattr(self.object.properties, prop_name, None)
            if isinstance(prop, UEReference):
                return prop.object_name
        return None

    def get_prop(self, prop_name: str) -> Any:
        if self.object is not None:
            return getattr(self.object.properties, prop_name, None)
        # if self.interface.properties is not None:
        #     return getattr(self.interface.properties, prop_name, None)
        return None

    def __repr__(self) -> str:
        return f"UEModel(interface={self.type}'{self.name}', object={self.get_name()})"
