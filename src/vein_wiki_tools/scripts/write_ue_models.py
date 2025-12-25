import asyncio
from pathlib import Path

import tqdm

from vein_wiki_tools.clients.file import create_page as f_create_page
from vein_wiki_tools.clients.pakdump.services import (
    get_categories,
    get_ue_model_by_path,
    prep_context_for_ue_model,
)
from vein_wiki_tools.data.models import Node
from vein_wiki_tools.data.pakdump.pakdump import pakdump_graph
from vein_wiki_tools.services.template import render
from vein_wiki_tools.services.wiki_pages import merge_pages, parse_page, render_page
from vein_wiki_tools.utils.file_helper import get_output_path
from vein_wiki_tools.utils.logging import getLogger

logger = getLogger(__name__)


LOGS_PATH = get_output_path("logs")
LOCAL_WIKI_PATH = get_output_path("wiki")


async def main() -> None:
    logger.info("Starting UE model wiki page writer")
    graph = await pakdump_graph(data=None)
    logger.debug(f"Graph has {len(graph.nodes)} nodes")

    # Filter models for writables
    models_to_write: list[tuple[Node, dict]] = []
    for node in tqdm.tqdm(graph.nodes.values(), desc="Filtering .."):
        if node.ue_model.model_info.template is None:
            continue
        logger.info(f"Filtering, at: {node.ue_model.display_name()}")
        context = await prep_context_for_ue_model(node=node, graph=graph)
        if not context["infobox"].infobox_template:
            logger.warning(
                f"Missing infobox template for {node.ue_model.display_name()}"
            )
            continue
        models_to_write.append((node, context))

    # Render pages
    for n, c in tqdm.tqdm(models_to_write, desc="Writing .."):
        ue_model = n.ue_model
        logger.info(f"Rendering {ue_model.display_name()}")
        content = await render(
            template=f"{ue_model.model_info.template}.jinja", context=c
        )
        subfolder = ue_model.model_info.template
        if ue_model.model_info.super_type is not None:
            subfolder = ue_model.model_info.super_type
        if ue_model.model_info.sub_type is not None:
            subfolder = ue_model.model_info.sub_type
        await f_create_page(
            path=LOCAL_WIKI_PATH
            / subfolder
            / f"{ue_model.model_info.console_name}.wiki",
            text=content,
            summary=f"Creating page for UE model: {ue_model.get_object_name()}",
        )

    # Generate stats comparing old version

    # Backup from wiki
    if False:
        pass

    # Write to wiki
    if False:
        pass


if __name__ == "__main__":
    asyncio.run(main())
