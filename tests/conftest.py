from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from vein_wiki_tools.utils import file_helper


@pytest.fixture
def testfiles():
    return Path(__file__).parent / "testfiles"


@pytest.fixture(autouse=True)
async def mock_vein_root(mocker: MockerFixture, testfiles: Path):
    mocker.patch.object(
        file_helper,
        file_helper.get_vein_root.__name__,
        autospec=True,
        return_value=testfiles,
    )
