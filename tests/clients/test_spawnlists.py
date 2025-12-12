from pathlib import Path

from vein_wiki_tools.clients.pakdump.services import get_ue_model_by_path
from vein_wiki_tools.clients.pakdump.spawnlists import UEItemList, UEItemSpawnlist


async def test_import_spawnlist(testfiles: Path):
    path = testfiles / "Vein" / "Spawnlists" / "ItemListCollections" / "02Dismantling" / "ILC_Ammo_Object.json"
    ue_model = get_ue_model_by_path(path)
    assert isinstance(ue_model, UEItemSpawnlist)
    assert ue_model.name == "ILC_Ammo_Object"
    assert len(ue_model.properties.lists) == 2
    assert ue_model.properties.lists[0].list.object_name == "ItemList'IL_ScrapPlastic'"


async def test_import_itemlist(testfiles: Path):
    path = testfiles / "Vein" / "Spawnlists" / "ItemLists" / "IL_Gunpowder.json"
    ue_model = get_ue_model_by_path(path)
    assert isinstance(ue_model, UEItemList)
    assert ue_model.name == "IL_Gunpowder"
    assert len(ue_model.properties.items) == 1
    assert ue_model.properties.items[0].item.object_name == "BlueprintGeneratedClass'BP_Gunpowder_C'"
