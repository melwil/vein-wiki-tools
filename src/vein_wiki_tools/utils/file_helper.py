import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent


def get_vein_root() -> Path:
    VEIN_PAK_DUMP_ROOT = Path("/mnt/c/Users/havard/Downloads/Vein")
    return VEIN_PAK_DUMP_ROOT


def get_full_file_path(project_file_path: str) -> str:
    """
    Get the full path for a file relative to the "src/vein_wiki_tools" as base folder
    """
    return os.path.join(BASE_DIR, project_file_path)


def get_import_path(filename: str | None = None) -> Path:
    """
    Get the import path for a file relative to the "src/vein_wiki_tools" as base folder

    Equals <git_project_root>/import_files/example-import-file.txt
    """
    git_project_root = BASE_DIR
    import_dir = git_project_root / "import_files"
    if filename is not None:
        return import_dir / filename
    return import_dir


def get_output_path(filename: str | None = None) -> Path:
    """
    Get the output path for a file relative to the "src/vein_wiki_tools" as base folder

    Equals <git_project_root>/output_files/example-output-file.txt
    """
    git_project_root = BASE_DIR
    output_dir = git_project_root / "output_files"
    if filename is not None:
        return output_dir / filename
    return output_dir
