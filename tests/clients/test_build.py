from vein_wiki_tools.clients.pakdump.services import get_ue_model_by_path


async def test_get_uebuildobject(testfiles):
    path = testfiles / "Vein" / "BuildObjects" / "Utilities" / "BO_MakeshiftBattery.json"
    ue_model = get_ue_model_by_path(path)
    assert ue_model
