import asyncio
from pathlib import Path

from vein_wiki_tools.clients.file import create_page as f_create_page
from vein_wiki_tools.clients.pakdump.services import get_categories, get_ue_model_by_path, prep_context_for_ue_model
from vein_wiki_tools.data.pakdump.pakdump import pakdump_graph
from vein_wiki_tools.services.template import render
from vein_wiki_tools.services.wiki_pages import merge_pages, parse_page, render_page
from vein_wiki_tools.utils.file_helper import get_output_path
from vein_wiki_tools.utils.logging import getLogger

logger = getLogger(__name__)

VEIN_PAK_DUMP_ROOT = Path("/mnt/c/Users/havard/Downloads/Vein")
ITEMTYPES = VEIN_PAK_DUMP_ROOT / "ItemTypes"
ITEMS_ROOT = VEIN_PAK_DUMP_ROOT / "Items"
AMMO_ROOT = ITEMS_ROOT / "Ammo"
MAGAZINES_ROOT = AMMO_ROOT


async def main():
    logger.info("Starting UE model wiki page writer")
    graph = await pakdump_graph(data=None)
    logger.info(f"Graph has {len(graph.nodes)} nodes")
    for node in graph.nodes.values():
        if node.ue_model.template is None:
            continue
        logger.info(f"Writing UE model page for: {node.ue_model.console_name}")
        context = await prep_context_for_ue_model(node=node, graph=graph)
        content = await render(template=f"ue/{node.ue_model.template}.jinja", context=context)
        await f_create_page(
            path=get_output_path("wiki") / node.ue_model.template / f"{node.ue_model.console_name}.wiki",
            text=content,
            summary=f"Creating page for UE model: {node.ue_model.get_type_object_name()}",
        )


if __name__ == "__main__":
    asyncio.run(main())
