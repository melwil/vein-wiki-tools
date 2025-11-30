from enum import Enum, auto

from vein_wiki_tools.models.items import Item


class ItemSource(Enum):
    CSV = auto()


async def get_items(source: ItemSource = ItemSource.CSV) -> list[Item]:
    if source == ItemSource.CSV:
        from vein_wiki_tools.data.csv.load import csv_read
        from vein_wiki_tools.utils.file_helper import get_full_file_path

        file_path = get_full_file_path("import_files/vein_items_subset.csv")
        items = await csv_read(file_path)
        return items

    raise ValueError(f"Unsupported item source: {source}")
