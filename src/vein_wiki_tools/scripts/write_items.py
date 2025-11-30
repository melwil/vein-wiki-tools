import asyncio
import re

from vein_wiki_tools.clients.file import create_page as f_create_page
from vein_wiki_tools.clients.file import read_page as f_read_page
from vein_wiki_tools.services.items import get_items
from vein_wiki_tools.services.template import get_template
from vein_wiki_tools.services.wiki_pages import merge_pages, parse_page, render_page
from vein_wiki_tools.utils.logging import getLogger

logger = getLogger(__name__)


async def main():
    # site = pywikibot.Site("en", "vein")
    # user = site.user()
    # logger.info(f"Logged in as: {user}")

    items = await get_items()
    logger.info(f"Retrieved {len(items)} items")

    for item in items:
        if not item.name:
            logger.warning(f"Skipping item with missing name: {item.filename}")
            continue
        if item.category != "Ammo":
            continue

        # fetch ecxisting page
        existing_page = await f_read_page(item.filename.rstrip(".json"))
        if existing_page is not None:
            existing_page_parsed = await parse_page(existing_page)
        else:
            logger.debug(f"No existing page for item: {item.name}")
            return

        # render new page
        template = await get_template("item.jinja")  # Ensure template exists
        new_page = template.render(subject=item)
        new_page = re.sub(r"\n{3,}", "\n\n", new_page).strip()
        new_page_parsed = await parse_page(new_page)

        # merge with existing page
        merged_page_parsed = await merge_pages(
            existing_page_parsed,
            new_page_parsed,
        )
        merged_page_parsed_rendered = await render_page(merged_page_parsed)

        summary = f"Creating page for ammo item: {item.name}"
        await f_create_page(item.filename, item.name, merged_page_parsed_rendered, summary)


if __name__ == "__main__":
    asyncio.run(main())
