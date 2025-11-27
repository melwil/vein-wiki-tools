import logging
import re
from collections import defaultdict
from enum import Enum, auto

import pywikibot

logger = logging.getLogger(__name__)


async def get_page(name: str):
    site = pywikibot.Site("en", "vein")
    page = pywikibot.Page(site, name)
    return page


class ParserFlag(Enum):
    NONE = auto()
    TEMPLATE_START = auto()
    TEMPLATE_END = auto()
    TEMPLATE_COMPLETE = auto()
    SECTION = auto()


SECTION_RE = re.compile(r"^=+\s*(.+?)\s*=+\s*$")


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

        self.parts: list[str] = parts
        self.blocks: dict[str, list] = blocks


def is_control_line(line: str) -> tuple[ParserFlag, str | None]:
    line = line.strip()
    if match := SECTION_RE.match(line):
        return ParserFlag.SECTION, match.group(1)
    elif line.startswith("{{"):
        line = re.sub(r"^\{\{", "", line)
        if line.endswith("}}"):
            line = re.sub(r"\}\}$", "", line).strip()
            if line.endswith("start"):
                return ParserFlag.TEMPLATE_START, line[:-5].strip()
            elif line.endswith("end"):
                return ParserFlag.TEMPLATE_END, line[:-3].strip()
            else:
                return ParserFlag.TEMPLATE_COMPLETE, line.strip()
        else:
            return ParserFlag.TEMPLATE_START, line.strip()
    elif line.endswith("}}"):
        return ParserFlag.TEMPLATE_END, None
    else:
        return ParserFlag.NONE, None


async def parse_page(text: str) -> ParsedPage:
    pre_sections = True
    parsed_page = ParsedPage()
    expecting_next: ParserFlag = ParserFlag.NONE
    current: str = ""

    for line in text.splitlines():
        logger.debug(f"Processing line: {line}")
        line_flag, category_name = is_control_line(line)
        if line_flag == ParserFlag.NONE and category_name is None:
            if expecting_next == ParserFlag.NONE and pre_sections:
                current = "pre_sections"
                parsed_page.parts.append(current)
            parsed_page.blocks[current].append(line)
            continue
        if line_flag != ParserFlag.NONE and category_name is None:
            raise ValueError("Expected category name for control line")

        if line_flag == ParserFlag.TEMPLATE_START and category_name is not None:
            expecting_next = ParserFlag.TEMPLATE_END
            current = category_name
            parsed_page.parts.append(current)
            parsed_page.blocks[current].append(line)
            continue
        elif line_flag == ParserFlag.TEMPLATE_END and category_name is not None:
            if expecting_next != ParserFlag.TEMPLATE_END:
                raise ValueError("Unexpected template end")
            parsed_page.blocks[current].append(line)
            expecting_next = ParserFlag.NONE
            current = ""
            continue
        elif line_flag == ParserFlag.SECTION and category_name is not None:
            pre_sections = False
            expecting_next = ParserFlag.NONE
            current = category_name
            parsed_page.parts.append(current)
            parsed_page.blocks[current].append(line)
            continue
        else:
            logger.error(f"Unhandled parser state: {line_flag}, {category_name}")
            raise ValueError("Unhandled parser state")

    logger.debug(f"Parsed page parts: {parsed_page.parts}")
    return parsed_page
