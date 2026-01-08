import json

from tests.data.pakdump.test_pakdump import create_pakdump_data
from vein_wiki_tools.clients.pakdump import services
from vein_wiki_tools.clients.pakdump.consumables import UEFluidDefinition
from vein_wiki_tools.clients.pakdump.models import UEBlueprintGeneratedClass, UEReference
from vein_wiki_tools.clients.pakdump.tools import UETool
from vein_wiki_tools.data.models import Node
from vein_wiki_tools.data.pakdump import pakdump
from vein_wiki_tools.models.common import WeaponInfobox


async def test_get_bullet_info():
    data = create_pakdump_data()
    await pakdump.import_bullet_types(data)
    await pakdump.import_ammo(data)
    await pakdump.import_magazines(data)
    await pakdump.import_firearms(data)
    wolfram_node = data.graph.get_node("BlueprintGeneratedClass'BP_Firearm_Flock17_C'", ue_model_type=UEBlueprintGeneratedClass)
    assert wolfram_node is not None
    bullet_info = services.get_bullet_info(wolfram_node, data.graph)
    assert bullet_info is not None
    assert bullet_info[0] == "9mm Round"
    assert bullet_info[1] == "22"


async def test_get_categories():
    data = create_pakdump_data()
    await pakdump.import_bullet_types(data)
    await pakdump.import_ammo(data)
    await pakdump.import_magazines(data)
    await pakdump.import_firearms(data)
    wolfram_node = data.graph.get_node("BlueprintGeneratedClass'BP_Firearm_Flock17_C'", ue_model_type=UEBlueprintGeneratedClass)
    assert wolfram_node is not None
    categories = await services.get_categories(node=wolfram_node, graph=data.graph)
    assert isinstance(categories, set)


async def test_get_magazine_capacity_string_for_flock17():
    data = create_pakdump_data()
    await pakdump.import_magazines(data)
    await pakdump.import_firearms(data)
    wolfram_node = data.graph.get_node("BlueprintGeneratedClass'BP_Firearm_Flock17_C'", ue_model_type=UEBlueprintGeneratedClass)
    assert wolfram_node is not None
    magazine_capacity_string = services.get_magazine_capacity_string(wolfram_node)
    assert magazine_capacity_string == "[[Wolfram_17_Magazine_-_17_Round|17 Rounds]]<br>[[Wolfram_17_Magazine_-_34_Round|34 Rounds]]"


async def test_get_magazine_capacity_string_for_mosinnagant():
    data = create_pakdump_data()
    await pakdump.import_magazines(data)
    await pakdump.import_firearms(data)
    mosin_node = data.graph.get_node("BlueprintGeneratedClass'BP_Firearm_MosinNagant_C'", ue_model_type=UEBlueprintGeneratedClass)
    assert mosin_node is not None
    magazine_capacity_string = services.get_magazine_capacity_string(mosin_node)
    assert magazine_capacity_string == "5 Rounds"


async def test_get_dismantling_results():
    dismantling_results = UEReference(
        object_name="ItemSpawnlist'ILC_Ammo_Object'",
        object_path="Vein/Content/Vein/Spawnlists/ItemListCollections/02Dismantling/ILC_Ammo_Object.0",
    )
    dismantling_results = await services.get_dismantling_results(dismantling_results)
    assert dismantling_results is not None
    assert len(dismantling_results.results) == 2
    assert dismantling_results.tools == []
    assert dismantling_results.min == 1
    assert dismantling_results.max == 2
    assert dismantling_results.results[0].items[0].text == "Plastic Scrap"
    assert dismantling_results.results[0].items[0].min == 1
    assert dismantling_results.results[0].items[0].max == 5
    assert dismantling_results.results[1].items[0].text == "Gunpowder"
    assert dismantling_results.results[1].items[0].min == 1
    assert dismantling_results.results[1].items[0].max == 5


async def test_get_dismantling_results_magazine():
    dismantling_results = UEReference(
        object_name="ItemSpawnlist'ILC_Metal_Machinery_Small'",
        object_path="Vein/Content/Vein/Spawnlists/ItemListCollections/02Dismantling/ILC_Metal_Machinery_Small.0",
    )
    dismantling_results = await services.get_dismantling_results(dismantling_results)
    assert dismantling_results is not None
    assert len(dismantling_results.results) == 2
    assert dismantling_results.tools == []
    assert dismantling_results.min == 1
    assert dismantling_results.max == 1
    assert len(dismantling_results.results) == 2
    assert len(dismantling_results.results[0].items) == 2
    assert dismantling_results.results[0].items[0].text == "Iron Scrap"
    assert dismantling_results.results[0].items[0].min == 1
    assert dismantling_results.results[0].items[0].max == 5
    assert len(dismantling_results.results[1].items) == 3
    assert dismantling_results.results[1].items[0].text == "Screws"
    assert dismantling_results.results[1].items[0].min == 2
    assert dismantling_results.results[1].items[0].max == 7


async def test_get_repair_requirements(testfiles):
    path = testfiles / "Vein" / "Items" / "Weapons" / "Ranged" / "BP_Firearm_Flock17.json"
    ue_model = services.get_ue_model_by_path(path)
    repair = await services.get_repair_requirements(Node(ue_model=ue_model))
    assert repair is not None
    assert repair.materials[0].text == "Iron Scrap"
    assert repair.tools is not None
    assert repair.tools[0].text == "Screwdriver"


async def test_get_type(testfiles):
    path = testfiles / "Vein" / "Tools" / "T_BasicCutting.json"
    ue_raw_model = json.loads(path.read_text())
    _type = services.get_type(ue_raw_model=ue_raw_model)
    assert _type == UETool


async def test_get_scavenging_info_wine_bottle(testfiles):
    data = create_pakdump_data()
    await pakdump.import_fluids(data)
    await pakdump.import_fluid_containers(data)
    wine_node = data.graph.get_node("BlueprintGeneratedClass'BP_WineBottle_C'", ue_model_type=UEBlueprintGeneratedClass)
    assert wine_node is not None
    scavenging = await services.get_scavenging_info(node=wine_node, graph=data.graph)
    assert scavenging is not None
    assert len(scavenging.fluid_contents) > 0
    assert scavenging.fluid_contents[0].fluid_type.text == "Wine"


async def test_get_scavenging_info_fl_steroids(testfiles):
    data = create_pakdump_data()
    await pakdump.import_fluids(data)
    await pakdump.import_fluid_containers(data)
    steroid_node = data.graph.get_node("FluidDefinition'FL_AnabolicSteroid'", ue_model_type=UEFluidDefinition)
    assert steroid_node is not None
    scavenging = await services.get_scavenging_info(node=steroid_node, graph=data.graph)
    assert scavenging is not None
    assert len(scavenging.fluids_contained) == 1


async def test_get_conditions_beer(testfiles):
    path = testfiles / "Vein" / "Fluids" / "FL_Beer.json"
    ue_model = services.get_ue_model_by_path(path)
    all_conditions = await services.get_conditions(ue_model=ue_model)
    assert len(all_conditions.drink) == 1
    assert all_conditions.drink[0].blood_sugar_impact == 10.0
    assert len(all_conditions.drink[0].conditions) == 2
    assert all_conditions.drink[0].addiction[0].amount == 8.0


async def test_get_conditions_steroids(testfiles):
    path = testfiles / "Vein" / "Fluids" / "FL_AnabolicSteroid.json"
    ue_model = services.get_ue_model_by_path(path)
    all_conditions = await services.get_conditions(ue_model=ue_model)
    assert len(all_conditions.inject) == 1
    assert all_conditions.inject[0].blood_sugar_impact == 0.0
    assert len(all_conditions.inject[0].conditions) == 1
    assert len(all_conditions.inject[0].xp_gain) == 2
    assert all_conditions.inject[0].xp_gain[0].text == "Strength"
    assert all_conditions.inject[0].xp_gain[1].text == "Throwing"


async def test_get_conditions_cold_medicine(testfiles):
    path = testfiles / "Vein" / "Fluids" / "FL_ColdMedicine.json"
    ue_model = services.get_ue_model_by_path(path)
    all_conditions = await services.get_conditions(ue_model=ue_model)
    assert len(all_conditions.inject) == 1
    assert all_conditions.inject[0].blood_sugar_impact == 0.0
    assert len(all_conditions.inject[0].conditions) == 2


async def test_get_infobox_melee_weapon(testfiles):
    data = create_pakdump_data()
    path = testfiles / "Vein" / "Items" / "Weapons" / "Melee" / "Crafted"
    await pakdump.import_folder(data=data, path=path)
    claw_sword_node = data.graph.get_node("BlueprintGeneratedClass'BP_Melee_ClawSword_C'", ue_model_type=UEBlueprintGeneratedClass)
    assert claw_sword_node
    infobox = await services.get_infobox(node=claw_sword_node, graph=data.graph)
    assert isinstance(infobox, WeaponInfobox)
    assert infobox.melee_damage_type == "Bladed"
