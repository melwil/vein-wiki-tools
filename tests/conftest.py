from pathlib import Path

import pytest
from pytest_mock import MockerFixture


@pytest.fixture
def testfiles():
    return Path(__file__).parent / "testfiles"


@pytest.fixture(autouse=True)
def mock_vein_root(mocker: MockerFixture, testfiles: Path):
    mocker.patch(
        "vein_wiki_tools.utils.file_helper.get_vein_root",
        return_value=testfiles / "Vein",
    )
