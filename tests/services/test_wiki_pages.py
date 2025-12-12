from collections import deque
from pathlib import Path

import pytest

from vein_wiki_tools.data.csv.load import csv_read
from vein_wiki_tools.services.template import get_template
from vein_wiki_tools.services.wiki_pages import ParserFlag, find_section_header_size, get_page, is_control_line, parse_categories, parse_infobox, parse_page, parse_sections
from vein_wiki_tools.utils.file_helper import get_full_file_path


@pytest.mark.skip(reason="only manual with proper cookie")
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
async def test_template_start(input: str, expected_category_name: str):
    line_flag, category_name = is_control_line(input)
    assert line_flag == ParserFlag.TEMPLATE_START
    assert category_name is not None
    assert category_name == expected_category_name


@pytest.mark.parametrize(
    "input,expected_category_name",
    [
        (r"}}", ""),
        (r"{{ template end }}", "template"),
    ],
)
async def test_template_end(input: str, expected_category_name: str):
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
async def test_template_complete(input: str, expected_category_name: str):
    line_flag, category_name = is_control_line(input)
    assert line_flag == ParserFlag.TEMPLATE_COMPLETE
    assert category_name == expected_category_name


@pytest.mark.parametrize(
    "input,expected_category_name",
    [
        (r"== Overview ==", "overview"),
        (r"=== Overview ===", "overview"),
        (r"=== More Info ==", "= more info"),
    ],
)
async def test_section_header(input: str, expected_category_name: str):
    line_flag, category_name = is_control_line(input)
    assert line_flag == ParserFlag.SECTION
    assert category_name == expected_category_name


async def test_parse_infobox():
    wiki_infobox = """{{Infobox Item
| something = Test Item
}}"""
    q = deque()
    q.extend(wiki_infobox.splitlines())
    infobox = await parse_infobox(q)
    assert infobox.name == "infobox"
    assert len(infobox.lines) == 3


@pytest.mark.parametrize(
    "input,expected_size",
    [
        (r"== Overview ==", 2),
        (r"=== Overview ===", 3),
        (r"=== More Info ==", 2),
    ],
)
async def test_find_header_size(input: str, expected_size: int):
    header_size = await find_section_header_size(input)
    assert header_size == expected_size


async def test_parse_sections():
    wiki_section = """== Overview ==
This is the overview section.
There's one more line in here.
{{ AndATemplate }}"""
    q = deque()
    q.extend(wiki_section.splitlines())
    sections = await parse_sections(q)
    assert sections is not None
    assert sections.name == "overview"
    assert len(sections.lines) == 4


async def test_parse_section_with_children():
    wiki_section = """== Overview ==
This is the overview section.
=== Here is a subsection ===
This is the subsection content.
=== Another subsection without content ==="""
    q = deque()
    q.extend(wiki_section.splitlines())
    sections = await parse_sections(q)
    assert sections is not None
    assert sections.name == "overview"
    assert len(sections.lines) == 2
    assert len(sections.children) == 2
    assert list(sections.children.values())[0].name == "here is a subsection"
    assert len(list(sections.children.values())[0].lines) == 2
    assert list(sections.children.values())[1].name == "another subsection without content"
    assert len(list(sections.children.values())[1].lines) == 1


async def test_parse_categories():
    wiki_categories = """[[Category:Test Category]]
[[Category:Another Category]]"""
    q = deque()
    q.extend(wiki_categories.splitlines())
    categories = await parse_categories(q)
    assert len(categories) == 2
    assert categories[0] == "[[Category:Test Category]]"
    assert categories[1] == "[[Category:Another Category]]"


async def test_parse_sections_wiki_article():
    test_wiki_file_path = get_full_file_path("tests/testfiles/BP_Melee_Shovel")
    content = Path(test_wiki_file_path).read_text()
    parsed_page = await parse_page(content)

    assert parsed_page.infobox is not None
    assert parsed_page.infobox.name == "infobox"
    assert parsed_page.infobox.lines[1].strip() == "| class       = custom"
    assert len(parsed_page.infobox.lines) == 3
    assert parsed_page.part_count() == 5  # infobox, pre_section, sections, categories


@pytest.mark.skip(reason="skip until we get here again")
async def test_render_and_parse_file():
    test_item_path = get_full_file_path("tests/testfiles/vein_items_shovel.csv")
    test_item = (await csv_read(filepath=test_item_path))[0]
    template = await get_template("item.jinja")
    rendered = template.render(subject=test_item)
    parsed = await parse_page(rendered)
    assert parsed.infobox is not None
