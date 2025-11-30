from pydantic import Field

from vein_wiki_tools.base import RootSchema


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


# FileName
# Name
# Description
# Category
# Weight
# Stackable
# StackSize,Capacity,ScentStrength,CompostQuality,HungerSatisfaction,ThirstAddition,DaystoDecay,RottenScentStrength,RepairTools,RepairIngredient1_Name,RepairIngredient1_Qty,RepairIngredient2_Name,RepairIngredient2_Qty,RepairIngredient3_Name,RepairIngredient3_Qty,RepairIngredient4_Name,RepairIngredient4_Qty,DismantleResult1_Name,DismantleResult1_MinQty,DismantleResult1_MaxQty,DismantleResult2_Name,DismantleResult2_MinQty,DismantleResult2_MaxQty,DismantleResult3_Name,DismantleResult3_MinQty,DismantleResult3_MaxQty,DismantleResult4_Name,DismantleResult4_MinQty,DismantleResult4_MaxQty,DismantleResult5_Name,DismantleResult5_MinQty,DismantleResult5_MaxQty,DismantleResult6_Name,DismantleResult6_MinQty,DismantleResult6_MaxQty,DismantleResult7_Name,DismantleResult7_MinQty,DismantleResult7_MaxQty,DismantleResult8_Name,DismantleResult8_MinQty,DismantleResult8_MaxQty,DismantleResult9_Name,DismantleResult9_MinQty,DismantleResult9_MaxQty,DismantleResult10_Name,DismantleResult10_MinQty,DismantleResult10_MaxQty,DismantleResult11_Name,DismantleResult11_MinQty,DismantleResult11_MaxQty,DismantleResult12_Name,DismantleResult12_MinQty,DismantleResult12_MaxQty,DismantleResult13_Name,DismantleResult13_MinQty,DismantleResult13_MaxQty,DismantleResult14_Name,DismantleResult14_MinQty,DismantleResult14_MaxQty,DismantleResult15_Name,DismantleResult15_MinQty,DismantleResult15_MaxQty,DismantleResult16_Name,DismantleResult16_MinQty,DismantleResult16_MaxQty,DismantleResult17_Name,DismantleResult17_MinQty,DismantleResult17_MaxQty,DismantleResult18_Name,DismantleResult18_MinQty,DismantleResult18_MaxQty,DismantleResult19_Name,DismantleResult19_MinQty,DismantleResult19_MaxQty,DismantleResult20_Name,DismantleResult20_MinQty,DismantleResult20_MaxQty,DismantleResult21_Name,DismantleResult21_MinQty,DismantleResult21_MaxQty,DismantleResult22_Name,DismantleResult22_MinQty,DismantleResult22_MaxQty,DismantleResult23_Name,DismantleResult23_MinQty,DismantleResult23_MaxQty,DismantleResult24_Name,DismantleResult24_MinQty,DismantleResult24_MaxQty,DismantleResult25_Name,DismantleResult25_MinQty,DismantleResult25_MaxQty,DismantleResult26_Name,DismantleResult26_MinQty,DismantleResult26_MaxQty,DismantleResult27_Name,DismantleResult27_MinQty,DismantleResult27_MaxQty,DismantleResult28_Name,DismantleResult28_MinQty,DismantleResult28_MaxQty,DismantleResult29_Name,DismantleResult29_MinQty,DismantleResult29_MaxQty,DismantleResult30_Name,DismantleResult30_MinQty,DismantleResult30_MaxQty,DismantleResult31_Name,DismantleResult31_MinQty,DismantleResult31_MaxQty,DismantleResult32_Name,DismantleResult32_MinQty,DismantleResult32_MaxQty,DismantleResult33_Name,DismantleResult33_MinQty,DismantleResult33_MaxQty,DismantleResult34_Name,DismantleResult34_MinQty,DismantleResult34_MaxQty,DismantleResult35_Name,DismantleResult35_MinQty,DismantleResult35_MaxQty,DismantleResult36_Name,DismantleResult36_MinQty,DismantleResult36_MaxQty
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
