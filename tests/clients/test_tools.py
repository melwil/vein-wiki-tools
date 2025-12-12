from pathlib import Path

from vein_wiki_tools.clients.pakdump.services import get_ue_model_by_path
from vein_wiki_tools.clients.pakdump.tools import UETool


async def test_import_basic_cutting(testfiles: Path):
    path = testfiles / "Vein" / "Tools" / "T_BasicCutting.json"
    ue_model = get_ue_model_by_path(path)
    assert isinstance(ue_model, UETool)
    assert ue_model.name == "T_BasicCutting"
