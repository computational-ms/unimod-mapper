import pytest
import unimod_mapper
from pathlib import Path


@pytest.fixture
def init_basic_unimod_mapper():
    package_dir = Path(unimod_mapper.__file__).parent
    test_dir = Path(__file__).parent
    unimod_path = package_dir.joinpath("unimod.xml")
    usermod_path = test_dir.joinpath("usermod.xml")
    M = unimod_mapper.UnimodMapper(xml_file_list=[unimod_path, usermod_path])
    return M
