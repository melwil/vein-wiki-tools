from enum import Enum

from pydantic import Field

from vein_wiki_tools.clients.pakdump.models import UEBaseModel, UEModel, UEReference


class SpawnChance(Enum):
    COMMON = "ERarity::Common"
    LIKELY = "ERarity::Likely"
    UNCOMMON = "ERarity::Uncommon"
    RARE = "ERarity::Rare"
    VERY_RARE = "ERarity::VeryRare"


class UEItemCounts(UEBaseModel):
    min: int = Field(..., alias="min")
    max: int | None = Field(default=None, alias="max")


class UEItemListItem(UEBaseModel):
    item: UEReference = Field(..., alias="Item")
    item_count: UEItemCounts = Field(..., alias="ItemCount")
    spawn_chance: SpawnChance = Field(..., alias="SpawnChance")
    chance_to_not_spawn: float = Field(..., alias="ChanceToNotSpawn")


class UEItemListProperties(UEBaseModel):
    items: list[UEItemListItem] = Field(default_factory=list, alias="Items")


class UEItemList(UEModel):
    properties: UEItemListProperties = Field(..., alias="Properties")

    def object_name(self) -> str:
        return f"{self.type}'{self.name}'"


class UESpawnlist(UEBaseModel):
    list: UEReference = Field(..., alias="List")
    spawn_chance: SpawnChance = Field(..., alias="SpawnChance")
    chance_to_not_spawn: float = Field(..., alias="ChanceToNotSpawn")


class UEItemSpawnlistProperties(UEBaseModel):
    lists: list[UESpawnlist] = Field(default_factory=list, alias="Lists")
    item_count: UEItemCounts = Field(..., alias="ItemCount")


class UEItemSpawnlist(UEModel):
    properties: UEItemSpawnlistProperties = Field(..., alias="Properties")

    def object_name(self) -> str:
        return f"{self.type}'{self.name}'"
