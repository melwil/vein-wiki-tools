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

VEIN_VERSIONS = ["0.022h10"]


async def main() -> None:
    logger.info("Starting UE model wiki page writer")
    graph = await pakdump_graph(data=None)
    logger.debug(f"Graph has {len(graph.nodes)} nodes")

    # Filter models for writables
    models_to_write: list[tuple[Node, dict]] = []
    for node in tqdm.tqdm(graph.nodes.values(), desc="Filtering .."):
        if node.ue_model.model_info.template is None:
            # logger.warning(f"Missing template for {str(node.ue_model)}")
            continue
        # logger.info(f"Filtering, at: {node.ue_model.display_name()}")
        context = await prep_context_for_ue_model(node=node, graph=graph)
        if not context["infobox"].infobox_template:
            logger.warning(f"Missing infobox template for {node.ue_model.display_name()}")
            continue
        models_to_write.append((node, context))

    # Render pages
    for n, c in tqdm.tqdm(models_to_write, desc="Writing .."):
        ue_model = n.ue_model
        # logger.info(f"Rendering {ue_model.display_name()}")
        content = await render(template=f"{ue_model.model_info.template}.jinja", context=c)
        subfolder = ue_model.model_info.template
        if ue_model.model_info.super_type is not None:
            subfolder = ue_model.model_info.super_type
        if ue_model.model_info.sub_type is not None:
            subfolder = ue_model.model_info.sub_type
        await f_create_page(
            path=LOCAL_WIKI_PATH / subfolder / f"{ue_model.model_info.console_name}.wiki",
            text=content,
            summary=f"Creating page for UE model: {ue_model.get_object_name()}",
        )

    # Generate stats comparing old version
    previous_version = VEIN_VERSIONS[-1]
    previous_version_root = get_output_path(previous_version)
    new_files = updated = not_found = unchanged = 0
    verified_files: list[Path] = []
    if previous_version_root is not None and previous_version_root.is_dir():
        previous_version_files = list(previous_version_root.glob("**/*"))
        for previous_file in tqdm.tqdm(previous_version_files, f"Comparing to {previous_version}"):
            relative_path = previous_file.relative_to(previous_version_root)
            new_file_path = LOCAL_WIKI_PATH / relative_path
            if new_file_path.is_file():
                verified_files.append(new_file_path)
                if not compare_files(previous_file, new_file_path):
                    logger.info("Updated file: %s", str(relative_path))
                    updated += 1
                else:
                    unchanged += 1
            else:
                logger.info("Missing file: %s", str(relative_path))
                not_found += 1
    else:
        logger.info("Found no previous output to compare for version %s", previous_version)

    for file in LOCAL_WIKI_PATH.glob("**/*"):
        if file not in verified_files:
            relative_path = file.relative_to(LOCAL_WIKI_PATH)
            logger.info("New file: %s", str(relative_path))
            new_files += 1

    # Backup from wiki
    if False:
        pass

    # Write to wiki
    if False:
        pass


def compare_files(file1: Path, file2: Path) -> bool:
    """Compare two files for equality."""
    return file1.read_text() == file2.read_text()


if __name__ == "__main__":
    asyncio.run(main())
