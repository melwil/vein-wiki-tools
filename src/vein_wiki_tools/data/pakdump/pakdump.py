import logging
from dataclasses import dataclass

from vein_wiki_tools.clients.pakdump.ammo import UEBulletType
from vein_wiki_tools.clients.pakdump.models import UEBlueprintGeneratedClass, UEItemType, UEModel
from vein_wiki_tools.clients.pakdump.services import get_ue_model_by_path
from vein_wiki_tools.data.models import Graph
from vein_wiki_tools.models.common import LinkType
from vein_wiki_tools.utils.file_helper import get_vein_root

logger = logging.getLogger(__name__)

VEIN_PAK_DUMP_ROOT = get_vein_root()
ITEMTYPES = VEIN_PAK_DUMP_ROOT / "ItemTypes"
TOOL_ROOT = VEIN_PAK_DUMP_ROOT / "Tools"
ITEMS_ROOT = VEIN_PAK_DUMP_ROOT / "Items"
AMMO_ROOT = ITEMS_ROOT / "Ammo"
BULLET_ROOT = VEIN_PAK_DUMP_ROOT / "BulletTypes"
MAGAZINES_ROOT = AMMO_ROOT
FIREARMS_ROOT = ITEMS_ROOT / "Weapons" / "Ranged"


@dataclass
class PakdumpData:
    graph: Graph


async def pakdump_graph(data: PakdumpData | None = None) -> Graph:
    # setup
    if data is None:
        data = PakdumpData(graph=Graph())
    await import_from_pakdump(data)

    # import
    await import_itemtypes(data)
    await import_tool_groups(data)

    # firearms and ammo
    await import_bullet_types(data)
    await import_ammo(data)
    await import_magazines(data)
    await import_firearms(data)

    return data.graph


async def import_from_pakdump(data: PakdumpData) -> None:
    root = UEModel(type="ItemRoot", name="ItemRoot")  # type:ignore
    data.graph = Graph()
    root_node = data.graph.upsert(root)
    data.graph.root_node = root_node


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


async def import_ammo(data: PakdumpData) -> None:
    for ammo_file in AMMO_ROOT.glob("BP_Ammo_*.json"):
        logger.debug("Importing ammo from %s", ammo_file)
        ue_model = get_ue_model_by_path(ammo_file)
        if not isinstance(ue_model, UEBlueprintGeneratedClass):
            logger.warning(f"Expected BGC, found {type(ue_model)} when scanning ammo: {ammo_file}")
            continue
        ue_model.template = "ammo"
        ue_model.console_name = ammo_file.stem
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
        ue_model.template = "magazine"
        ue_model.console_name = magazine_file.stem
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
        ue_model.template = "firearm"
        ue_model.console_name = weapon_file.stem
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
