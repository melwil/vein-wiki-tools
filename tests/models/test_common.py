from vein_wiki_tools.models import get_subclass_type
from vein_wiki_tools.models.common import ItemCountReference, ItemMinMaxReference, WikiReference
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
