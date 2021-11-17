import os
import sys
import pytest

from pathlib import Path

TESTS_WORKING_DIR = Path(__file__).parent / "resources"
os.chdir(TESTS_WORKING_DIR)
sys.path.append(str(TESTS_WORKING_DIR))

from pab.config import load_configs
from pab.blockchain import Blockchain


@pytest.fixture
def blockchain():
    return Blockchain(TESTS_WORKING_DIR, load_configs(TESTS_WORKING_DIR))
