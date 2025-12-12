from pathlib import Path

from vein_wiki_tools.utils.file_helper import get_import_path
from vein_wiki_tools.utils.logging import getLogger

logger = getLogger(__name__)


async def create_page(path: Path, text: str, summary: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


async def edit_page(path: Path, text: str, summary: str):
    await create_page(path, text, summary)


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
