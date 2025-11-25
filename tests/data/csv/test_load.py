from vein_wiki_tools.data.csv.load import csv_read
from vein_wiki_tools.utils.file_helper import get_full_file_path


async def test_csv_read():
    test_file_path = get_full_file_path("tests/data/csv/vein_items_subset.csv")
    item_list = await csv_read(test_file_path)
    assert len(item_list) == 2
