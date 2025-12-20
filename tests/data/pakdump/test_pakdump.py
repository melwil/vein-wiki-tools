from vein_wiki_tools.clients.pakdump.consumables import UEFluidDefinition
from vein_wiki_tools.clients.pakdump.firearms import UEBulletType
from vein_wiki_tools.clients.pakdump.models import UEBlueprintGeneratedClass, UEItemType, UEModel
from vein_wiki_tools.clients.pakdump.services import get_related_models
from vein_wiki_tools.clients.pakdump.tools import UETool
from vein_wiki_tools.data.models import Graph
from vein_wiki_tools.data.pakdump.pakdump import (
    PakdumpData,
    import_all,
    import_ammo,
    import_bullet_types,
    import_firearms,
    import_fluids,
    import_itemtypes,
    import_magazines,
    import_tool_groups,
    pakdump_graph,
)
from vein_wiki_tools.models.common import LinkType


def create_pakdump_data() -> PakdumpData:
    data = PakdumpData(graph=Graph())
    root_node = data.graph.upsert(UEModel(type="ItemRoot", name="ItemRoot"))
    data.graph.root_node = root_node
    return data


async def test_pakdump_graph():
    graph = await pakdump_graph()
    assert graph.root_node is not None
    assert graph.root_node.ue_model.name == "ItemRoot"


async def test_itemtypes():
    data = create_pakdump_data()
    await import_itemtypes(data)
    assert data.graph.root_node is not None
    itemtype_edges = data.graph.root_node.edges

    assert len(itemtype_edges) == 10
    for linktype, node in itemtype_edges:
        if linktype == LinkType.HAS_ITEM_TYPE:
            assert isinstance(node.ue_model, UEItemType)
            assert node.ue_model.name.startswith("IT_")


async def test_tool_groups():
    data = create_pakdump_data()
    await import_tool_groups(data)
    tool_group_node_count = 0
    for node in data.graph.nodes.values():
        if isinstance(node.ue_model, UETool):
            assert node.ue_model.name.startswith("T_")
            tool_group_node_count += 1
    assert tool_group_node_count == 30


async def test_import_fluids():
    data = create_pakdump_data()
    await import_fluids(data)
    fluid_node_count = 0
    for node in data.graph.nodes.values():
        if isinstance(node.ue_model, UEFluidDefinition):
            assert node.ue_model.name.startswith("FL_")
            fluid_node_count += 1
    assert fluid_node_count == 33


async def test_import_bullet_types_from_pakdump():
    data = create_pakdump_data()
    await import_bullet_types(data)
    assert data.graph.root_node is not None
    bullet_type_node_count = 0
    for node in data.graph.nodes.values():
        if isinstance(node.ue_model, UEBulletType):
            if node.ue_model.name.startswith("BT_"):
                assert node.ue_model.properties.bullet_damage is not None
                bullet_type_node_count += 1

    assert bullet_type_node_count == 6


async def test_import_ammo_from_pakdump():
    data = create_pakdump_data()
    await import_ammo(data)
    assert data.graph.root_node is not None
    ammo_node_count = 0
    for node in data.graph.nodes.values():
        if isinstance(node.ue_model, UEBlueprintGeneratedClass):
            if node.ue_model.name.startswith("BP_Ammo_"):
                ammo_node_count += 1

    assert ammo_node_count == 13


async def test_import_ammo_from_pakdump_with_all_edges():
    data = create_pakdump_data()
    # await import_itemtypes(data)
    # await import_bullet_types(data)
    # await import_ammo(data)
    await import_all(data)
    assert data.graph.root_node is not None
    itemtype_ammo_node = data.graph.get_node("ItemType'IT_Ammo'", ue_model_type=UEItemType)
    assert itemtype_ammo_node is not None

    ammo_nodes = []
    for linktype, node in itemtype_ammo_node.neighbours:
        if node.ue_model.name.startswith("BP_Ammo_"):
            if linktype == LinkType.HAS_ITEM_TYPE:
                print(node.ue_model.name)
                assert isinstance(node.ue_model, UEBlueprintGeneratedClass)
                assert node.ue_model.model_info.sub_type == "bullet"
                ammo_nodes.append(node)
    assert len(ammo_nodes) == 13
    bullet_type_node_names = set()
    for ammo_node in ammo_nodes:
        for linktype, node in ammo_node.edges:
            if node.ue_model.name.startswith("BT_"):
                if linktype == LinkType.HAS_BULLET_TYPE:
                    assert isinstance(node.ue_model, UEBulletType)
                    bullet_type_node_names.add(node.ue_model.name)
    assert len(bullet_type_node_names) == 6


async def test_import_magazines_from_pakdump():
    data = create_pakdump_data()
    await import_magazines(data)
    assert data.graph.root_node is not None
    magazine_node_count = 0
    for node in data.graph.nodes.values():
        if isinstance(node.ue_model, UEModel):
            if node.ue_model.name.startswith("BP_Magazine_"):
                magazine_node_count += 1

    assert magazine_node_count == 10


async def test_import_firearms_from_pakdump():
    data = create_pakdump_data()
    await import_firearms(data)
    assert data.graph.root_node is not None
    firearm_node_count = 0
    for node in data.graph.nodes.values():
        if isinstance(node.ue_model, UEBlueprintGeneratedClass):
            if node.ue_model.name.startswith("BP_Firearm_"):
                firearm_node_count += 1
    assert firearm_node_count == 20


async def test_import_firearms_from_pakdump_with_all_edges():
    data = create_pakdump_data()
    await import_itemtypes(data)
    await import_magazines(data)
    await import_firearms(data)
    assert data.graph.root_node is not None
    itemtype_weapon_node = data.graph.get_node("ItemType'IT_Weapons'", ue_model_type=UEItemType)
    assert itemtype_weapon_node is not None
    weapon_edges = itemtype_weapon_node.neighbours

    # Find firearms from weapon type node
    weapon_nodes = []
    for linktype, node in weapon_edges:
        if node.ue_model.name.startswith("BP_Firearm_"):
            if linktype == LinkType.HAS_ITEM_TYPE:
                assert isinstance(node.ue_model, UEBlueprintGeneratedClass)
                assert node.ue_model.model_info.sub_type == "firearm"
                weapon_nodes.append(node)
    assert len(weapon_nodes) == 20

    # Find magazines related to firearms
    magazine_node_count = 0
    for weapon_node in weapon_nodes:
        related_magazines = get_related_models(weapon_node, LinkType.HAS_MAGAZINE)["edges"]
        for magazine_node in related_magazines:
            if magazine_node.ue_model.name.startswith("BP_Magazine_"):
                magazine_node_count += 1
    assert magazine_node_count == 10


async def test_import_drinks_with_fluids():
    data = create_pakdump_data()
    await import_all(data)
    wine_node = data.graph.get_node("BlueprintGeneratedClass'BP_WineBottle_C'", ue_model_type=UEBlueprintGeneratedClass)
    assert wine_node is not None
    for linktype, node in wine_node.edges:
        if linktype == LinkType.HAS_FLUID:
            assert node.ue_model.get_object_name() == "FluidDefinition'FL_Wine'"


async def test_import_all():
    data = create_pakdump_data()
    await import_all(data)
    assert len(data.graph.nodes) >= 255
