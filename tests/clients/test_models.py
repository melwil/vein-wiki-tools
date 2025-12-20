from pathlib import Path

import pytest

from vein_wiki_tools.clients.pakdump.models import UEBlueprintGeneratedClass, UEModelInfo, UEReference
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


async def test_get_ue_model_by_path(testfiles: Path):
    path = testfiles / "Vein" / "Items" / "Tools" / "BP_SleepingBag01.json"
    ue_model = get_ue_model_by_path(path)
    assert isinstance(ue_model, UEBlueprintGeneratedClass)
    assert ue_model.name == "BP_SleepingBag01_C"
    assert ue_model.object is not None


@pytest.mark.parametrize(
    ["ue_model_path", "expected_template"],
    [
        [Path("Vein") / "Items" / "Ammo" / "BP_Ammo_9mm.json", "item"],
        [Path("Vein") / "Items" / "Clothing" / "03_Jacket" / "BP_CL_MilitaryJacket.json", "item"],
        [Path("Vein") / "Recipes" / "Furnace" / "HCR_CopperIngot.json", None],
    ],
)
async def test_get_template(testfiles, ue_model_path: Path, expected_template: str | None):
    ue_root = testfiles / ue_model_path
    ue_model = get_ue_model_by_path(ue_root)
    assert ue_model.model_info.template == expected_template


async def test_model_info():
    model_info = UEModelInfo()
    model_info.categories.add("moo")
    assert isinstance(model_info.categories, set)
