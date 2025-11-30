import logging
import re
from collections import defaultdict, deque
from enum import Enum, auto

import pywikibot

logger = logging.getLogger(__name__)


async def get_page(name: str):
    site = pywikibot.Site("en", "vein")
    page = pywikibot.Page(site, name)
    return page


async def write_page(name: str, content: str, summary: str = ""):
    site = pywikibot.Site("en", "vein")
    page = pywikibot.Page(site, name)
    page.text = content
    page.save(summary=summary)


class ParserFlag(Enum):
    NONE = auto()
    TEMPLATE_START = auto()
    TEMPLATE_END = auto()
    TEMPLATE_COMPLETE = auto()
    SECTION = auto()
    CATEGORIES = auto()


class ParsedPage:
    def __init__(
        self,
        parts: list[str] | None = None,
        blocks: dict[str, list] | None = None,
    ):
        if parts is None:
            parts = list()
        if blocks is None:
            blocks = defaultdict(list)

        self.infobox: ParsedInfobox | None = None
        self.pre_section: ParsedText | None = None
        self.sections: dict[str, ParsedSection] = {}
        self.categories: list[str] = []

    def part_count(self) -> int:
        return sum(
            [
                self.infobox is not None,
                self.pre_section is not None,
                len(self.sections),
                len(self.categories),
            ]
        )


class ParsedInfobox:
    def __init__(
        self,
        name: str,
        lines: list[str] | None = None,
    ):
        if lines is None:
            lines = []

        self.name: str = name
        self.lines: list[str] = lines


class ParsedTemplate:
    def __init__(
        self,
        name: str,
        lines: list[str] | None = None,
    ):
        if lines is None:
            lines = []

        self.name: str = name
        self.lines: list[str] = lines


class ParsedText:
    def __init__(
        self,
        lines: list[str] | None = None,
    ):
        if lines is None:
            lines = []

        self.lines: list[str] = lines


class ParsedSection:
    def __init__(
        self,
        name: str,
        ordering: int = 0,
        header_size: int = 0,
        lines: list[str] | None = None,
    ):
        if lines is None:
            lines = []

        self.name: str = name
        self.header_size: int = header_size
        self.ordering: int = ordering
        self.lines: list[str] = lines
        self.children: dict[str, ParsedSection] = {}


SECTION_RE = re.compile(r"^\s*(=+)(.+?)\1\s*$")


def is_control_line(line: str) -> tuple[ParserFlag, str | None]:
    line = line.strip()
    if match := SECTION_RE.match(line):
        return ParserFlag.SECTION, match.group(2).strip().lower()
    elif line.startswith("{{"):
        line = re.sub(r"^\{\{", "", line)
        if line.endswith("}}"):
            line = re.sub(r"\}\}$", "", line).strip()
            if line.endswith("start"):
                return ParserFlag.TEMPLATE_START, line[:-5].strip().lower()
            elif line.endswith("end"):
                return ParserFlag.TEMPLATE_END, line[:-3].strip().lower()
            else:
                return ParserFlag.TEMPLATE_COMPLETE, line.strip().lower()
        else:
            return ParserFlag.TEMPLATE_START, line.strip().lower()
    elif line.endswith("}}"):
        return ParserFlag.TEMPLATE_END, ""
    elif line.startswith("[[Category:") and line.endswith("]]"):
        return ParserFlag.CATEGORIES, line[11:-2].strip().lower()
    else:
        return ParserFlag.NONE, None


async def parse_page(text: str) -> ParsedPage:
    pre_sections = True
    parsed_page = ParsedPage()
    q: deque[str] = deque()
    q.extend(text.splitlines())

    while len(q) > 0:
        line = q[0]
        logger.debug(f"Processing line: {line}")
        flag, category_name = is_control_line(line)
        if flag != ParserFlag.NONE and category_name is None:
            raise ValueError("Expected category name for control line")

        # infobox, other templates will be in sections for now
        if flag == ParserFlag.TEMPLATE_START and category_name is not None:
            if pre_sections and "infobox" in category_name.lower():
                category_name = "infobox"
                parsed_page.infobox = await parse_infobox(q)
            continue
        # sections
        elif flag == ParserFlag.SECTION and category_name is not None:
            pre_sections = False
            section = await parse_sections(q)
            if section is None:
                logger.error("Section parsing returned None")
                continue
            parsed_page.sections[section.name] = section
            continue
        # loose text before sections, i.e. pre_section
        elif flag == ParserFlag.NONE and category_name is None:
            if pre_sections:
                if parsed_page.pre_section is None:
                    parsed_page.pre_section = ParsedText()
                parsed_page.pre_section.lines.append(q.popleft())
                continue
            logger.debug(f"No place to put line, skipping: {q.popleft()}")
        # categories
        elif flag == ParserFlag.CATEGORIES and category_name is not None:
            parsed_page.categories.extend(await parse_categories(q))
            continue
        # unhandled
        else:
            logger.error(f"Unhandled parser state: {flag}, {category_name}")
            raise ValueError("Unhandled parser state")

    return parsed_page


async def parse_infobox(q: deque[str]) -> ParsedInfobox:
    infobox = ParsedInfobox(name="infobox")
    while len(q) > 0:
        line = q.popleft()
        infobox.lines.append(line)
        flag, _ = is_control_line(line)
        if flag == ParserFlag.TEMPLATE_END:
            break
    return infobox


async def find_section_header_size(line: str) -> int:
    match = SECTION_RE.match(line)
    if not match:
        raise ValueError("Line is not a section header")
    return len(match.group(1))


async def parse_sections(q: deque[str]) -> ParsedSection | None:
    section: ParsedSection | None = None
    header_size: int = 0
    while len(q) > 0:
        line = q[0]
        if section is None:
            if not line.lstrip().startswith("="):
                raise ValueError("Expected section header")
            header_size = await find_section_header_size(line)
            section = ParsedSection(name=line.strip("= ").lower(), header_size=header_size)
            section.lines.append(q.popleft())
            continue
        if section is None:
            raise ValueError("Section was not initialized properly")
        flag, _ = is_control_line(line)
        if flag == ParserFlag.CATEGORIES:
            break
        elif flag == ParserFlag.SECTION:
            if await find_section_header_size(q[0]) <= header_size:
                break
            child_section = await parse_sections(q)
            if child_section is not None:
                section.children[child_section.name] = child_section
            else:
                logger.error("Child section parsing returned None")
        else:
            section.lines.append(q.popleft())

    return section


async def parse_categories(q: deque[str]) -> list[str]:
    categories: list[str] = []
    while len(q) > 0:
        flag, _ = is_control_line(q[0])
        if flag != ParserFlag.CATEGORIES:
            break
        categories.append(q.popleft())
    return categories


async def merge_pages(original: ParsedPage, new: ParsedPage) -> ParsedPage:
    merged = ParsedPage()
    processed_parts = []

    logger.debug(f"Merging pages. Original parts: {original.part_count()}, New parts: {new.part_count()}")
    # infobox
    if original.infobox is not None and new.infobox is None:
        logger.debug("Keeping infobox from ORIGINAL")
        merged.infobox = original.infobox
    if new.infobox is not None:
        logger.debug("Updating infobox from NEW")
        merged.infobox = new.infobox
    processed_parts.append("infobox")

    # pre_section
    if original.pre_section is not None and new.pre_section is None:
        logger.debug("Keeping pre_section from ORIGINAL")
        merged.pre_section = original.pre_section
    if new.pre_section is not None:
        logger.debug("Updating pre_section from NEW")
        merged.pre_section = new.pre_section
    processed_parts.append("pre_section")

    # sections
    for section in original.sections:
        if section in new.sections:
            logger.debug(f"Merging section - from NEW: {section}")
            merged.sections[section] = new.sections[section]
            processed_parts.append(section)
        elif section in original.sections:
            logger.debug(f"Merging section - from ORIGINAL: {section}")
            merged.sections[section] = original.sections[section]
            processed_parts.append(section)
    for section in new.sections:
        if section not in processed_parts:
            logger.debug(f"Adding new section: {section}")
            merged.sections[section] = new.sections[section]

    # categories
    if original.categories and not new.categories:
        logger.debug("Keeping categories from ORIGINAL")
        merged.categories = original.categories
    if new.categories:
        logger.debug("Updating categories from NEW")
        merged.categories = new.categories

    return merged


async def render_page(parsed_page: ParsedPage) -> str:
    page = ""
    if parsed_page.infobox is not None:
        for line in parsed_page.infobox.lines:
            page += f"{line}\n"
    if parsed_page.pre_section is not None:
        for line in parsed_page.pre_section.lines:
            page += f"{line}\n"
    for section in parsed_page.sections:
        block_lines: list[str] = parsed_page.sections[section].lines
        page += "\n".join(block_lines) + "\n"
    for category in parsed_page.categories:
        page += f"{category}\n"
    return page.strip()
