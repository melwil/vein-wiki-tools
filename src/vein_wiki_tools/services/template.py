import re
from typing import Any

from jinja2 import Environment, PackageLoader, Template, select_autoescape

env = Environment(
    loader=PackageLoader("vein_wiki_tools", "templates"),
    autoescape=select_autoescape(),
)


async def get_template(template_name: str) -> Template:
    return env.get_template(template_name)


async def render(template: str, context: dict[str, Any]) -> str:
    rendered = env.get_template(template).render(context)
    rendered = trim_bad_newlines(rendered)
    return rendered


def trim_bad_newlines(text: str) -> str:
    start_pattern = r"^\s*\n"
    start_replacement = ""
    text = re.sub(start_pattern, start_replacement, text)
    mid_pattern = r"(\s*\n){3,}"
    mid_replacement = "\n\n"
    text = re.sub(mid_pattern, mid_replacement, text)
    end_pattern = r"\n\s*$"
    end_replacement = ""
    text = re.sub(end_pattern, end_replacement, text)
    return text
