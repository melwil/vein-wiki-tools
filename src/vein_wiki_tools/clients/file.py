from pathlib import Path

from vein_wiki_tools.utils.file_helper import get_import_path, get_output_path
from vein_wiki_tools.utils.logging import getLogger

logger = getLogger(__name__)


async def create_page(filename: str, name: str, text: str, summary: str):
    with open(get_output_path("wiki") / filename, "w", encoding="utf-8") as f:
        f.write(
            f"""
{text}
-------------------------
'''Summary:''' {summary}"""
        )


async def edit_page(filename: str, name: str, text: str, summary: str):
    await create_page(filename, name, text, summary)


async def read_page(
    filename: str | None = None,
    filepath: str | None = None,
) -> str | None:
    if filepath is None and filename is not None:
        path = get_import_path("wiki") / filename
        logger.debug(f"Reading wiki page from: {path}")
    elif filepath is not None:
        path = Path(filepath)
    else:
        ValueError("Either filename or filepath must be provided")

    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return None
