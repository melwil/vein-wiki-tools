import json

from tests.data.pakdump.test_pakdump import create_pakdump_data
from vein_wiki_tools.clients.pakdump.models import UEBlueprintGeneratedClass, UEReference
from vein_wiki_tools.clients.pakdump.services import get_bullet_info, get_dismantling_results, get_magazine_capacity_string, get_type
from vein_wiki_tools.clients.pakdump.tools import UETool
from vein_wiki_tools.data.pakdump.pakdump import import_ammo, import_bullet_types, import_firearms, import_magazines


async def test_get_bullet_info():
    data = create_pakdump_data()
    await import_bullet_types(data)
    await import_ammo(data)
    await import_magazines(data)
    await import_firearms(data)
    wolfram_node = data.graph.get_node("BlueprintGeneratedClass'BP_Firearm_Flock17_C'", ue_model_type=UEBlueprintGeneratedClass)
    assert wolfram_node is not None
    bullet_info = get_bullet_info(wolfram_node, data.graph)
    assert bullet_info is not None
    assert bullet_info[0] == "9mm Round"
    assert bullet_info[1] == "22"


async def test_get_magazine_capacity_string_for_flock17():
    data = create_pakdump_data()
    await import_magazines(data)
    await import_firearms(data)
    wolfram_node = data.graph.get_node("BlueprintGeneratedClass'BP_Firearm_Flock17_C'", ue_model_type=UEBlueprintGeneratedClass)
    assert wolfram_node is not None
    magazine_capacity_string = get_magazine_capacity_string(wolfram_node)
    assert magazine_capacity_string == "[[Wolfram_17_Magazine_-_17_Round|17 Rounds]]<br>[[Wolfram_17_Magazine_-_34_Round|34 Rounds]]"


async def test_get_magazine_capacity_string_for_mosinnagant():
    data = create_pakdump_data()
    await import_magazines(data)
    await import_firearms(data)
    mosin_node = data.graph.get_node("BlueprintGeneratedClass'BP_Firearm_MosinNagant_C'", ue_model_type=UEBlueprintGeneratedClass)
    assert mosin_node is not None
    magazine_capacity_string = get_magazine_capacity_string(mosin_node)
    assert magazine_capacity_string == "5 Rounds"


async def test_get_dismantling_results():
    dismantling_results = UEReference(
        object_name="ItemSpawnlist'ILC_Ammo_Object'",
        object_path="Vein/Content/Vein/Spawnlists/ItemListCollections/02Dismantling/ILC_Ammo_Object.0",
    )
    dismantling_results = await get_dismantling_results(dismantling_results)
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


async def test_get_type(testfiles):
    path = testfiles / "Vein" / "Tools" / "T_BasicCutting.json"
    ue_raw_model = json.loads(path.read_text())
    _type = get_type(ue_raw_model=ue_raw_model)
    assert _type == UETool
