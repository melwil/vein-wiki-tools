from pathlib import Path

import pytest

from vein_wiki_tools.clients.file import read_page
from vein_wiki_tools.services.wiki_pages import ParserFlag, get_page, is_control_line, parse_page
from vein_wiki_tools.utils.file_helper import get_full_file_path


async def test_get_page():
    page_name = ".38 Special"
    page = await get_page(page_name)
    assert page.title == page_name


@pytest.mark.parametrize(
    "input,expected_category_name",
    [
        (r"{{template", "template"),
        (r"{{ template start }}", "template"),
        (r"{{template start}}", "template"),
        (r"{{ template start }}", "template"),
    ],
)
async def test_template_start(input: str, expected_category_name: str | None):
    line_flag, category_name = is_control_line(input)
    assert line_flag == ParserFlag.TEMPLATE_START
    assert category_name is not None
    assert category_name == expected_category_name


@pytest.mark.parametrize(
    "input,expected_category_name",
    [
        (r"}}", None),
        (r"{{ template end }}", "template"),
    ],
)
async def test_template_end(input: str, expected_category_name: str | None):
    line_flag, category_name = is_control_line(input)
    assert line_flag == ParserFlag.TEMPLATE_END
    assert category_name == expected_category_name


@pytest.mark.parametrize(
    "input,expected_category_name",
    [
        (r"{{template}}", "template"),
        (r"{{ template }}", "template"),
    ],
)
async def test_template_complete(input: str, expected_category_name: str | None):
    line_flag, category_name = is_control_line(input)
    assert line_flag == ParserFlag.TEMPLATE_COMPLETE
    assert category_name == expected_category_name


@pytest.mark.parametrize(
    "input,expected_category_name",
    [
        (r"== Overview ==", "Overview"),
        (r"=== Overview ===", "Overview"),
    ],
)
async def test_section_header(input: str, expected_category_name: str | None):
    line_flag, category_name = is_control_line(input)
    assert line_flag == ParserFlag.SECTION
    assert category_name == expected_category_name


async def test_parse_sections():
    wiki_section = """== Overview ==
This is the overview section."""
    sections = await parse_page(wiki_section)

    assert len(sections.blocks) == 1
    assert sections.blocks["Overview"] == [
        "== Overview ==",
        "This is the overview section.",
    ]


async def test_parse_sections_wiki_article():
    test_wiki_file_path = get_full_file_path("tests/testfiles/BP_Melee_Shovel")
    content = Path(test_wiki_file_path).read_text()
    sections = await parse_page(content)

    assert len(sections.blocks) == 6
    assert sections.parts == ["Infobox", "pre_sections", "More Attributes", "Acquiring", "Use", "Building", "Dismantling"]


async def test_parse_sections_file():
    test_item_path = get_full_file_path("tests/testfiles/vein_items_shovel.csv")
    test_item = await read_page(filepath=test_item_path)
    pass
