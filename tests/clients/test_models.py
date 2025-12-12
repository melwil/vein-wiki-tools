from pathlib import Path

from vein_wiki_tools.clients.pakdump.models import UEBlueprintGeneratedClass, UEReference
from vein_wiki_tools.clients.pakdump.services import get_ue_model_by_path, get_ue_model_by_reference


async def test_ue_model(testfiles: Path):
    path = testfiles / "Vein" / "Items" / "Ammo" / "BP_Ammo_9mm.json"
    ue_model = get_ue_model_by_path(path)
    assert isinstance(ue_model, UEBlueprintGeneratedClass)
    assert ue_model.name == "BP_Ammo_9mm_C"
    assert ue_model.object is not None
    assert ue_model.object.name == "Default__BP_Ammo_9mm_C"
    assert str(ue_model.object.properties.name) == "9mm Round"
    assert str(ue_model.object.properties.name) == ue_model.object.properties.name.source_string  # type: ignore


async def test_ue_model_by_reference(testfiles: Path):
    model_reference = UEReference(
        object_name="BlueprintGeneratedClass'BP_Ammo_9mm_C'",
        object_path="Vein/Content/Vein/Items/Ammo/BP_Ammo_9mm.0",
    )
    ue_model = get_ue_model_by_reference(model_reference, _root=testfiles / "Vein")

    assert isinstance(ue_model, UEBlueprintGeneratedClass)
    assert ue_model.name == "BP_Ammo_9mm_C"
    assert ue_model.object is not None
    assert ue_model.object.name == "Default__BP_Ammo_9mm_C"
    assert str(ue_model.object.properties.name) == "9mm Round"
    assert ue_model.get_prop("stackable")
