from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Type

from pydantic import ConfigDict, Field

from vein_wiki_tools.base import RootSchema


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


class LinkType(Enum):
    HAS_BULLET_TYPE = "HAS_BULLETTYPE"
    HAS_ITEM_TYPE = "HAS_ITEMTYPE"
    HAS_AMMO = "HAS_AMMO"
    HAS_MAGAZINE = "HAS_MAGAZINE"
    HAS_CRAFTING_RECIPE = "HAS_CRAFTING_RECIPE"
    HAS_COOKING_RECIPE = "HAS_COOKING_RECIPE"
    HAS_SCHEMATIC = "HAS_SCHEMATIC"
    HAS_DISMANTLE_RESULT = "HAS_DISMANTLE_RESULT"


class Link(RootSchema):
    from_node_id: str = Field(..., serialization_alias="FromNodeID")
    to_node_id: str = Field(..., serialization_alias="ToNodeID")
    link_type: LinkType = Field(..., serialization_alias="LinkType")


class Category(NodeContent):
    name: str = Field(..., serialization_alias="Name")
    sync_to_wiki: bool = Field(..., serialization_alias="SyncToWiki")


@dataclass
class Infobox:
    title: str | None = None
    image: str | None = None
    description: str | None = None
    weight: str | None = None
    item_id: str | None = None


@dataclass
class ItemInfobox(Infobox):
    stackable: bool = False
    stack_size: int | None = None
    renewable: bool | None = None

    def stackable_str(self) -> str:
        if not self.stackable:
            return "No"
        return f"Yes ({self.stack_size if self.stack_size else 50})"

    def renewable_str(self) -> str:
        return ""


@dataclass
class WeaponInfobox(Infobox):
    firearm_damage: str | None = None
    ammo_capacity: str | None = None
    ammo_type: str | None = None
    melee_damage_type: str | None = None
    melee_swing_time: str | None = None
    melee_base_damage: str | None = None
    melee_base_dps: str | None = None


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
class DismantleResult:
    items: list[ItemMinMaxReference]


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
        self.max = max_count or 0
        self.results = results or []

    def is_valid(self) -> bool:
        return len(self.results) > 0 and self.min >= 0 and self.max >= self.min

    def tools_str(self) -> str:
        if not self.tools:
            return "No tool required"
        return "<br>".join(str(tool) for tool in self.tools)

    def rolls_str(self) -> str:
        return f"{self.min} - {self.max}"

    def results_str(self) -> str:
        result_lines = []
        for result in self.results:
            item_set = []
            for item in result.items:
                item_set.append(str(item))
            result_lines.append("<br>".join(item_set))
        return "<br>".join(result_lines)
