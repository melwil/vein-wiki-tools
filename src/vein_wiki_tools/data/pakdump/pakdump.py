import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Generator

import tqdm

from vein_wiki_tools.clients.pakdump.consumables import UEFluidDefinition
from vein_wiki_tools.clients.pakdump.firearms import UEBulletType
from vein_wiki_tools.clients.pakdump.models import (
    UEBlueprintGeneratedClass,
    UEItemType,
    UEModel,
)
from vein_wiki_tools.clients.pakdump.services import get_ue_model_by_path
from vein_wiki_tools.clients.pakdump.tools import UETool
from vein_wiki_tools.data.models import Graph
from vein_wiki_tools.models.common import LinkType
from vein_wiki_tools.utils.file_helper import get_vein_root

logger = logging.getLogger(__name__)

VEIN_PAK_DUMP_ROOT = get_vein_root()
ITEMTYPES = VEIN_PAK_DUMP_ROOT / "ItemTypes"
BULLET_ROOT = VEIN_PAK_DUMP_ROOT / "BulletTypes"
TOOL_ROOT = VEIN_PAK_DUMP_ROOT / "Tools"
FLUIDS_ROOT = VEIN_PAK_DUMP_ROOT / "Fluids"
ITEMS_ROOT = VEIN_PAK_DUMP_ROOT / "Items"
AMMO_ROOT = ITEMS_ROOT / "Ammo"
MAGAZINES_ROOT = AMMO_ROOT
FIREARMS_ROOT = ITEMS_ROOT / "Weapons" / "Ranged"
CLOTHES_ROOT = ITEMS_ROOT / "Clothing"
CONSUMABLES_ROOT = ITEMS_ROOT / "Consumables"
DRINKS_ROOT = CONSUMABLES_ROOT / "01Drink"
DRINKS_CAR_ROOT = DRINKS_ROOT / "Car"
DRINKS_CLEANING_ROOT = DRINKS_ROOT / "Cleaning"
DRINKS_MEDICAL_ROOT = DRINKS_ROOT / "Medical"
DRINKS_PANTRY_ROOT = DRINKS_ROOT / "Pantry"
MEDICAL_ROOT = ITEMS_ROOT / "Medical"


@dataclass
class PakdumpData:
    graph: Graph


async def pakdump_graph(data: PakdumpData | None = None) -> Graph:
    # setup
    if data is None:
        data = PakdumpData(graph=Graph())
    await import_from_pakdump(data)

    # # import types and categories
    # await import_itemtypes(data)
    # await import_tool_groups(data)
    # await import_fluids(data)

    # # firearms and ammo
    # await import_bullet_types(data)
    # await import_ammo(data)
    # await import_magazines(data)
    # await import_firearms(data)

    # # clothing
    # await import_clothing(data)

    # # fluid containers
    # await import_fluid_containers(data)

    return data.graph


async def import_from_pakdump(data: PakdumpData) -> None:
    root = UEModel(type="ItemRoot", name="ItemRoot")  # type:ignore
    data.graph = Graph()
    root_node = data.graph.upsert(root)
    data.graph.root_node = root_node
    await import_all(data)


async def import_itemtypes(data: PakdumpData) -> None:
    if not (root_node := data.graph.root_node):
        raise ValueError("Graph has no root node")

    for itemtype_file in ITEMTYPES.glob("IT_*.json"):
        ue_model = get_ue_model_by_path(path=itemtype_file)
        itemtype_node = data.graph.upsert(ue_model)
        root_node.add_edge(LinkType.HAS_ITEM_TYPE, itemtype_node)


async def import_bullet_types(data: PakdumpData) -> None:
    for bullet_file in BULLET_ROOT.glob("BT_*.json"):
        logger.debug("Importing bullet type from %s", bullet_file)
        ue_model = get_ue_model_by_path(bullet_file)
        data.graph.upsert(ue_model, update=True)


async def import_tool_groups(data: PakdumpData) -> None:
    for tool_file in TOOL_ROOT.glob("T_*.json"):
        logger.debug("Importing tool from %s", tool_file)
        ue_model = get_ue_model_by_path(path=tool_file)
        data.graph.upsert(ue_model, update=True)


async def import_fluids(data: PakdumpData) -> None:
    for fluid_file in FLUIDS_ROOT.glob("FL_*.json"):
        logger.debug("Importing fluid from %s", fluid_file)
        ue_model = get_ue_model_by_path(path=fluid_file)
        ue_model.model_info.console_name = fluid_file.stem
        data.graph.upsert(ue_model, update=True)


async def import_ammo(data: PakdumpData) -> None:
    for ammo_file in AMMO_ROOT.glob("BP_Ammo_*.json"):
        logger.debug("Importing ammo from %s", ammo_file)
        ue_model = get_ue_model_by_path(ammo_file)
        if not isinstance(ue_model, UEBlueprintGeneratedClass):
            logger.warning(f"Expected BGC, found {type(ue_model)} when scanning ammo: {ammo_file}")
            continue
        ue_model.model_info.console_name = ammo_file.stem
        ammo_node = data.graph.upsert(ue_model)
        if itemtype_node := data.graph.get_node(
            key=ue_model.get_type_object_name(),
            ue_model_type=UEItemType,
        ):
            ammo_node.add_edge(LinkType.HAS_ITEM_TYPE, itemtype_node)
        if bullet_type := ue_model.get_prop("bullet_type"):
            if bullet_node := data.graph.get_node(
                key=bullet_type.object_name,
                ue_model_type=UEBulletType,
            ):
                ammo_node.add_edge(LinkType.HAS_BULLET_TYPE, bullet_node)


async def import_magazines(data: PakdumpData) -> None:
    for magazine_file in MAGAZINES_ROOT.glob("BP_Magazine_*.json"):
        logger.debug("Importing magazine from %s", magazine_file)
        ue_model = get_ue_model_by_path(magazine_file)
        if not isinstance(ue_model, UEBlueprintGeneratedClass):
            logger.warning(f"Expected BGC, found {type(ue_model)} when scanning magazine: {magazine_file}")
            continue
        ue_model.model_info.console_name = magazine_file.stem
        magazine_node = data.graph.upsert(ue_model)
        if itemtype_node := data.graph.get_node(
            key=ue_model.get_type_object_name(),
            ue_model_type=UEItemType,
        ):
            magazine_node.add_edge(LinkType.HAS_ITEM_TYPE, itemtype_node)
        if bullet_type_name := ue_model.get_prop_object_name("bullet_type"):
            if ammo_node := data.graph.get_node(
                key=bullet_type_name,
                ue_model_type=UEBlueprintGeneratedClass,
            ):
                magazine_node.add_edge(LinkType.HAS_AMMO, ammo_node)


async def import_firearms(data: PakdumpData) -> None:
    for weapon_file in FIREARMS_ROOT.glob("BP_Firearm_*.json"):
        logger.debug("Importing firearm from %s", weapon_file)
        ue_model = get_ue_model_by_path(weapon_file)
        if not isinstance(ue_model, UEBlueprintGeneratedClass):
            logger.warning(f"Expected BGC, found {type(ue_model)} when scanning weapon: {weapon_file}")
            continue
        ue_model.model_info.console_name = weapon_file.stem
        weapon_node = data.graph.upsert(ue_model)
        if itemtype_node := data.graph.get_node(
            key=ue_model.get_type_object_name(),
            ue_model_type=UEItemType,
        ):
            weapon_node.add_edge(LinkType.HAS_ITEM_TYPE, itemtype_node)
        if magazine_items := ue_model.get_prop("magazine_items"):
            for magazine in magazine_items:
                if magazine_node := data.graph.get_node(
                    key=magazine.object_name,
                    ue_model_type=UEBlueprintGeneratedClass,
                ):
                    weapon_node.add_edge(LinkType.HAS_MAGAZINE, magazine_node)


async def import_clothing(data: PakdumpData):
    pass
    # for fluid_file in CLOTHES_ROOT.glob("BP_CL_*.json"):
    #     logger.debug("Importing fluid from %s", fluid_file)
    #     ue_model = get_ue_model_by_path(path=fluid_file)
    #     data.graph.upsert(ue_model, update=True)


async def import_fluid_containers(data: PakdumpData):
    await import_fluid_container_category(data, DRINKS_ROOT)
    await import_fluid_container_category(data, DRINKS_CAR_ROOT)
    await import_fluid_container_category(data, DRINKS_CLEANING_ROOT)
    await import_fluid_container_category(data, DRINKS_MEDICAL_ROOT)
    await import_fluid_container_category(data, DRINKS_PANTRY_ROOT)


async def import_fluid_container_category(
    data: PakdumpData,
    import_folder: Path,
):
    for file in import_folder.glob("BP_*.json"):
        ue_model = get_ue_model_by_path(file)
        if not isinstance(ue_model, UEBlueprintGeneratedClass):
            logger.warning(f"Expected BGC, found {type(ue_model)} when scanning fluid containers: {file}")
            continue
        ue_model.model_info.console_name = file.stem
        fluid_container_node = data.graph.upsert(ue_model)
        if itemtype_node := data.graph.get_node(
            key=ue_model.get_type_object_name(),
            ue_model_type=UEItemType,
        ):
            fluid_container_node.add_edge(LinkType.HAS_ITEM_TYPE, itemtype_node)
        if fluid_type := ue_model.get_prop("fluid_type"):
            if fluid_node := data.graph.get_node(
                key=fluid_type.object_name,
                ue_model_type=UEFluidDefinition,
            ):
                fluid_container_node.add_edge(LinkType.HAS_FLUID, fluid_node)

    # # import types and categories
    # -await import_itemtypes(data)
    # -await import_tool_groups(data)
    # -await import_fluids(data)

    # # firearms and ammo
    # -await import_bullet_types(data)
    # -await import_ammo(data)
    # -await import_magazines(data)
    # -await import_firearms(data)

    # # clothing
    # -await import_clothing(data)

    # # fluid containers
    # -await import_fluid_containers(data)


folders = (
    ("BuildObjects", "ALL"),
    # "ItemTypes",
    # "BulletTypes",
    # "Fluids",
    # "Tools",
    # ("Items", ("Ammo", "Tools")),
    # (
    #     "Items",
    #     (
    #         "Clothing",
    #         (
    #             "01_Head",
    #             "02_Face",
    #             "03_Jacket",
    #             "04a_Upper",
    #             "04b_UpperArmor",
    #             "05a_Lower",
    #             "05b_LowerArmor",
    #             "06_Feet",
    #             "07_Hands",
    #             "08_Back",
    #             "09_FullBody",
    #         ),
    #     ),
    # ),
    # ("Items", ("Consumables", ("01Drink", "ALL"))),
    # ("Items", ("Weapons", "ALL")),
)


def get_folder(path: Path, subfolders: tuple) -> Generator[Path]:
    for sf in subfolders:
        if isinstance(sf, Path):
            yield sf
            continue
        if isinstance(sf, tuple):
            if len(sf) == 1:
                yield from get_folder(path=path, subfolders=sf)
                continue
            if isinstance(sf[1], tuple):
                yield from get_folder(path=path / sf[0], subfolders=sf[1:])
                continue
            elif sf[1] == "ALL":
                subpath = path / sf[0]
                yield from get_folder(
                    path=subpath,
                    subfolders=tuple(p for p in subpath.glob("**/*") if p.is_dir()),
                )
                yield from get_folder(path=path, subfolders=(sf[0],))
                continue
            else:
                yield from get_folder(path=path, subfolders=sf)
                continue
        if not isinstance(sf, str):
            continue
        logger.debug(f"Yielding: {path / sf}")
        yield path / sf


async def import_all(data: PakdumpData) -> None:
    logger.info("Starting import all")
    all_folders = list(get_folder(VEIN_PAK_DUMP_ROOT, folders))
    for folder in tqdm.tqdm(all_folders, desc="Importing folders.."):
        await import_folder(data=data, path=folder)


async def import_folder(data: PakdumpData, path: Path) -> None:
    if not (root_node := data.graph.root_node):
        raise ValueError("Graph has no root node")

    num_files_in_folder = 0
    for file in path.glob("*.json"):
        # skip these conditions
        if re.match(r"Meshes|OLD", file.parent.name):
            continue
        if re.match(r"(NS|HDP|SM)_.*", file.stem):
            continue
        if re.match(r".*/BuildObjects/.*BP_.*", str(file)):
            continue
        if file.stem.startswith("T_Thumb"):
            continue

        # logger.debug(f"Processing {file}")
        ue_model = get_ue_model_by_path(file)
        ue_model.model_info.console_name = file.stem
        node = data.graph.upsert(ue_model)

        num_files_in_folder += 1

        # Item types
        if ue_model.type == "ItemType":
            root_node.add_edge(LinkType.HAS_ITEM_TYPE, node)

        if itemtype_node := data.graph.get_node(
            key=ue_model.get_type_object_name(),
            ue_model_type=UEItemType,
        ):
            node.add_edge(LinkType.HAS_ITEM_TYPE, itemtype_node)

        # Other connections

        # Link fluid containers spawning contents to the fluid
        if fluid_type := ue_model.get_prop("fluid_type"):
            if fluid_node := data.graph.get_node(
                key=fluid_type.object_name,
                ue_model_type=UEFluidDefinition,
            ):
                node.add_edge(LinkType.HAS_FLUID, fluid_node)
        # The type of magazine for a firearm
        if magazine_items := ue_model.get_prop("magazine_items"):
            for magazine in magazine_items:
                if fluid_node := data.graph.get_node(
                    key=magazine.object_name,
                    ue_model_type=UEBlueprintGeneratedClass,
                ):
                    node.add_edge(LinkType.HAS_MAGAZINE, fluid_node)
        # The type of ammo for a magazine
        if ue_model.model_info.sub_type == "magazine":
            if bullet_type := ue_model.get_prop("bullet_type"):
                if bullet_node := data.graph.get_node(
                    key=bullet_type.object_name,
                    ue_model_type=UEBlueprintGeneratedClass,
                ):
                    if isinstance(bullet_node.ue_model, UEBlueprintGeneratedClass):
                        node.add_edge(LinkType.HAS_AMMO, bullet_node)
        # The bullet type for ammo
        if ue_model.model_info.sub_type == "bullet":
            if bullet_type := ue_model.get_prop("bullet_type"):
                if bullet_node := data.graph.get_node(
                    key=bullet_type.object_name,
                    ue_model_type=UEBulletType,
                ):
                    if isinstance(bullet_node.ue_model, UEBulletType):
                        node.add_edge(LinkType.HAS_BULLET_TYPE, bullet_node)

    logger.info(f"Imported {num_files_in_folder} files from {path}")
