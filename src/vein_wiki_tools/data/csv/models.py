import re
from typing import Any

from pydantic import Field, ValidationInfo, model_validator

from vein_wiki_tools.base import RootSchema
from vein_wiki_tools.models.items import Item
from vein_wiki_tools.utils.metrology import imperial_to_metric


class CsvItem(RootSchema):
    filename: str = Field(..., alias="FileName")
    name: str = Field(..., alias="Name")
    description: str = Field(..., alias="Description")
    category: str = Field(..., alias="Category")
    weight: float = Field(..., alias="Weight")
    stackable: bool | None = Field(default=None, alias="Stackable")
    stack_size: int | None = Field(default=None, alias="StackSize")
    capacity: int | None = Field(default=None, alias="Capacity")
    scent_strength: int | None = Field(default=None, alias="ScentStrength")
    compost_quality: int | None = Field(default=None, alias="CompostQuality")
    hunger_satisfaction: int | None = Field(default=None, alias="HungerSatisfaction")
    thirst_addition: int | None = Field(default=None, alias="ThirstAddition")
    days_to_decay: int | None = Field(default=None, alias="DaystoDecay")
    rotten_scent_strength: int | None = Field(default=None, alias="RottenScentStrength")
    repair_tools: str | None = Field(default=None, alias="RepairTools")

    @model_validator(mode="before")
    @classmethod
    def validate_empty_strings(cls, data: Any, info: ValidationInfo) -> Any:
        if isinstance(data, str):
            return strings_equal_to_none(data)
        if isinstance(data, list):
            return [strings_equal_to_none(v) for v in data]
        if isinstance(data, dict):
            return {k: strings_equal_to_none(v) for k, v in data.items()}
        return data

    def to_item(self) -> Item:
        return Item(
            filename=self.filename,
            name=self.name,
            description=re.sub(r"\s{2,}", "<br><br>", self.description).strip(),
            category=self.category,
            weight_lbs=self.weight,
            weight_kg=imperial_to_metric(pounds=self.weight),
            stackable=self.stackable or False,
            stack_size=self.stack_size,
            capacity=self.capacity,
            scent_strength=self.scent_strength,
            compost_quality=self.compost_quality,
            hunger_satisfaction=self.hunger_satisfaction,
            thirst_addition=self.thirst_addition,
            days_to_decay=self.days_to_decay,
            rotten_scent_strength=self.rotten_scent_strength,
            repair_tools=self.repair_tools,
        )


def strings_equal_to_none(v: Any) -> Any:
    if v == "" or v == "0" or v == "null" or v == "undefined" or v == "None" or v == "NaN" or v == "[]" or v == "{}" or v == "()" or v == "''" or v == '""' or v == "N/A" or v == r"N\/A":
        return None
    return v
