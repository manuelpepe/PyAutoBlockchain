import os
import sys
import pytest

from pathlib import Path

TESTS_WORKING_DIR = Path(__file__).parent / "resources"
os.chdir(TESTS_WORKING_DIR)
sys.path.append(str(TESTS_WORKING_DIR))

from pab.exceptions import MissingConfig

try:
    from pab.config import APP_CONFIG
    APP_CONFIG.get('endpoint')
except MissingConfig as err:
    print("ERROR: Config not found. Create config with valid rpc to run tests.")
    raise err

from pab.blockchain import Blockchain
from pab.queue import QueueLoader


@pytest.fixture
def blockchain():
    return Blockchain(APP_CONFIG.get('endpoint'), 137, "POLYGON")


@pytest.fixture
def queue(blockchain):
    return QueueLoader(blockchain).load()
