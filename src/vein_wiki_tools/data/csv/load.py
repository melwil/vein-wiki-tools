import aiofiles
from aiocsv import AsyncDictReader

from vein_wiki_tools.data.csv.models import CsvItem
from vein_wiki_tools.models.items import DismantleResult, Item, RepairIngredient


async def csv_read(
    filepath: str,
    delimiter: str = ",",
    quotechar: str = '"',
) -> list[Item]:
    item_list: list[Item] = []
    async with aiofiles.open(filepath, mode="r", encoding="utf-8", newline="") as afp:
        async for row in AsyncDictReader(afp, delimiter=delimiter, quotechar=quotechar):
            item = to_item(row)  # type: ignore
            item_list.append(item)
    return item_list


def to_item(csv_item: dict) -> Item:
    repair_ingredients: list[RepairIngredient] = []
    for i in range(1, 5):
        name = csv_item.get(f"RepairIngredient{i}_Name")
        qty = csv_item.get(f"RepairIngredient{i}_Qty")
        if name and qty:
            repair_ingredients.append(RepairIngredient(name=name, quantity=int(qty)))

    dismantle_results: list[DismantleResult] = []
    for i in range(1, 37):
        name = csv_item.get(f"DismantleResult{i}_Name")
        min_qty = csv_item.get(f"DismantleResult{i}_MinQty")
        max_qty = csv_item.get(f"DismantleResult{i}_MaxQty")
        if name and min_qty and max_qty:
            dismantle_results.append(
                DismantleResult(
                    name=name,
                    min_quantity=min_qty,
                    max_quantity=max_qty,
                )
            )

    parsed_csv_item = CsvItem.model_validate(csv_item)
    item = parsed_csv_item.to_item()
    item.repair_ingredients = repair_ingredients
    item.dismantle_results = dismantle_results

    return item
