from pathlib import Path

from vein_wiki_tools.clients.pakdump.recipes import UEBaseRecipe, UEHeatConverterRecipe
from vein_wiki_tools.clients.pakdump.services import get_ue_model_by_path


async def test_import_cooking_recipe(testfiles: Path):
    path = testfiles / "Vein" / "Recipes" / "Cooking" / "Pot" / "RP_MichiganSauce.json"
    ue_model = get_ue_model_by_path(path)
    assert isinstance(ue_model, UEBaseRecipe)
    assert ue_model.name == "RP_MichiganSauce"


async def test_import_crafting_recipe(testfiles: Path):
    path = testfiles / "Vein" / "Recipes" / "Crafting" / "Parts" / "CR_MetalBrackets.json"
    ue_model = get_ue_model_by_path(path)
    assert isinstance(ue_model, UEBaseRecipe)
    assert ue_model.name == "CR_MetalBrackets"


async def test_import_furnace_recipe(testfiles: Path):
    path = testfiles / "Vein" / "Recipes" / "Furnace" / "HCR_CopperIngot.json"
    ue_model = get_ue_model_by_path(path)
    assert isinstance(ue_model, UEHeatConverterRecipe)
    assert ue_model.name == "HCR_CopperIngot"


async def test_import_charcoalkiln_recipe(testfiles: Path):
    path = testfiles / "Vein" / "Recipes" / "CharcoalKiln" / "HCR_RefinedCharcoal.json"
    ue_model = get_ue_model_by_path(path)
    assert isinstance(ue_model, UEHeatConverterRecipe)
    assert ue_model.name == "HCR_RefinedCharcoal"
