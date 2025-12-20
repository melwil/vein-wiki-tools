from vein_wiki_tools.models import get_subclass_type
from vein_wiki_tools.models.common import ItemCountReference, ItemMinMaxReference, WikiReference, get_wiki_fluid_capacity_string, get_wiki_fluid_span_string, get_wiki_weight_string
from vein_wiki_tools.models.items import Ammo


async def test_get_subclass_type():
    wanted_type = Ammo
    result = get_subclass_type("Ammo")

    assert result == wanted_type


async def test_wiki_reference():
    ref = WikiReference(
        link="Plastic_Scrap",
        text="Plastic Scrap",
    )
    assert str(ref) == "[[Plastic_Scrap|Plastic Scrap]]"


async def test_item_count_reference():
    ref = ItemCountReference(
        link="Plastic_Scrap",
        text="Plastic Scrap",
        count=3,
    )
    assert str(ref) == "3× [[Plastic_Scrap|Plastic Scrap]]"


async def test_item_min_max_reference():
    ref = ItemMinMaxReference(
        link="Plastic_Scrap",
        text="Plastic Scrap",
        min=1,
        max=5,
    )
    assert str(ref) == "1-5× [[Plastic_Scrap|Plastic Scrap]]"


async def test_get_wiki_weight_string():
    result = get_wiki_weight_string(pounds=10)
    assert result == "10.00 lbs / 4.54 kg"


async def test_get_wiki_fluid_capacity_string_l():
    result = get_wiki_fluid_capacity_string(fluid_ml=5000)
    assert result == "175.975 fl. oz. / 5.0 L"


async def test_get_wiki_fluid_capacity_string_1000_mL():
    result = get_wiki_fluid_capacity_string(fluid_ml=1000)
    assert result == "35.195 fl. oz. / 1000.0 mL"


async def test_get_wiki_fluid_span_string_ml():
    result = get_wiki_fluid_span_string(fluid_ml_min=100, fluid_ml_max=1000)
    assert result == "3.520-35.195 fl. oz.<br>100.0-1000.0 mL"


async def test_get_wiki_fluid_span_string_L():
    result = get_wiki_fluid_span_string(fluid_ml_min=100, fluid_ml_max=10000)
    assert result == "3.520-351.951 fl. oz.<br>0.1-10.0 L"
