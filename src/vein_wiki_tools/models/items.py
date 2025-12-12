from enum import Enum

from pydantic import Field

from vein_wiki_tools.base import RootSchema
from vein_wiki_tools.models.common import NodeContent
from vein_wiki_tools.utils.metrology import imperial_to_metric


class DismantleResult(RootSchema):
    name: str = Field(..., serialization_alias="Name")
    min_quantity: int = Field(..., serialization_alias="MinQty")
    max_quantity: int = Field(..., serialization_alias="MaxQty")


class RecipeIngredient(RootSchema):
    name: str = Field(..., serialization_alias="Name")
    quantity: int = Field(..., serialization_alias="Quantity")


class RepairIngredient(RootSchema):
    name: str = Field(..., serialization_alias="Name")
    quantity: int = Field(..., serialization_alias="Qty")


# For Items from google sheet csv
class Item(RootSchema):
    filename: str = Field(..., serialization_alias="FileName")
    name: str = Field(..., serialization_alias="Name")
    description: str = Field(..., serialization_alias="Description")
    category: str = Field(..., serialization_alias="Category")
    weight_lbs: float = Field(..., serialization_alias="Weight (lbs)")
    weight_kg: float = Field(..., serialization_alias="Weight (kg)")
    stackable: bool = Field(default=False, serialization_alias="Stackable")
    stack_size: int | None = Field(default=None, serialization_alias="StackSize")
    capacity: int | None = Field(default=None, serialization_alias="Capacity")
    scent_strength: int | None = Field(default=None, serialization_alias="ScentStrength")
    compost_quality: int | None = Field(default=None, serialization_alias="CompostQuality")
    hunger_satisfaction: int | None = Field(default=None, serialization_alias="HungerSatisfaction")
    thirst_addition: int | None = Field(default=None, serialization_alias="ThirstAddition")
    days_to_decay: int | None = Field(default=None, serialization_alias="DaystoDecay")
    rotten_scent_strength: int | None = Field(default=None, serialization_alias="RottenScentStrength")
    repair_tools: str | None = Field(default=None, serialization_alias="RepairTools")
    repair_ingredients: list[RepairIngredient] = Field(
        default_factory=list,
        serialization_alias="RepairIngredients",
    )
    dismantle_results: list[DismantleResult] = Field(
        default_factory=list,
        serialization_alias="DismantleResults",
    )
    crafting_ingredients: list[RecipeIngredient] = Field(
        default_factory=list,
        serialization_alias="CraftingIngredients",
    )


class BulletType(Enum):
    BT_9MM = "9mm"
    BT_45ACP = ".45 ACP"
    BT_57MM = "5.7mm"
    BT_40SW = ".40 S&W"
    BT_223REM = ".223 Remington"
    BT_556MM = "5.56mm"
    BT_300BLK = ".300 Blackout"
    BT_308WIN = ".308 Winchester"
    BT_762MM = "7.62mm"
    BT_50AE = ".50 AE"
    BT_50BMG = ".50 BMG"
    BT_12G = "12 Gauge"


class ItemRoot(NodeContent):
    # Simply the root node for the item graph
    object_name_s: str = Field(default="ItemRoot")


class Color(RootSchema):
    r: float = Field(..., serialization_alias="R", validation_alias="R")
    g: float = Field(..., serialization_alias="G", validation_alias="G")
    b: float = Field(..., serialization_alias="B", validation_alias="B")
    a: float = Field(..., serialization_alias="A", validation_alias="A")
    hex: str = Field(..., serialization_alias="Hex", validation_alias="Hex")


class ItemType(NodeContent):
    type: str = Field(...)
    name: dict[str, str] = Field(..., serialization_alias="Name")
    icon: dict[str, str] = Field(..., serialization_alias="Icon", validation_alias="Icon")
    color: Color = Field(..., serialization_alias="Color", validation_alias="Color")
    order: int | None = Field(default=None, serialization_alias="Order", validation_alias="Order")


class Ammo(NodeContent):
    type: str = Field(..., serialization_alias="FileName")
    name: str = Field(..., serialization_alias="Name", validation_alias="Name")
    description: str = Field(..., serialization_alias="Description")
    stackable: bool = Field(default=False, serialization_alias="Stackable")
    stack_size: int | None = Field(default=None, serialization_alias="StackSize")
    weight_lbs: float = Field(..., serialization_alias="Weight (lbs)")

    @property
    def weight_kg(self) -> float | None:
        return imperial_to_metric(pounds=self.weight_lbs)


class Magazine(NodeContent):
    type: str = Field(..., serialization_alias="FileName")
    name: str = Field(..., serialization_alias="Name", validation_alias="Name")
    description: str = Field(..., serialization_alias="Description")
    stackable: bool = Field(default=False, serialization_alias="Stackable")
    stack_size: int | None = Field(default=None, serialization_alias="StackSize")
    weight_lbs: float = Field(..., serialization_alias="Weight (lbs)")

    @property
    def weight_kg(self) -> float | None:
        return imperial_to_metric(pounds=self.weight_lbs)
