import os
import sys
import pytest

from pathlib import Path

TESTS_WORKING_DIR = Path(__file__).parent / "resources"
os.chdir(TESTS_WORKING_DIR)
sys.path.append(str(TESTS_WORKING_DIR))

from pab.config import APP_CONFIG
from pab.blockchain import Blockchain
from pab.queue import QueueLoader


@pytest.fixture
def blockchain():
    return Blockchain(APP_CONFIG.get('endpoint'), 137, "POLYGON")


@pytest.fixture
def queue(blockchain):
    return QueueLoader(blockchain).load()
