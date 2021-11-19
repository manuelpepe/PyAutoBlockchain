import os
import sys
import pytest

from contextlib import contextmanager
from tempfile import TemporaryDirectory

from pathlib import Path
from pab.accounts import load_accounts
from pab.init import chdir


TESTS_WORKING_DIR = Path(__file__).parent / "resources"
os.chdir(TESTS_WORKING_DIR)
sys.path.append(str(TESTS_WORKING_DIR))

from pab.config import load_configs
from pab.blockchain import Blockchain


@pytest.fixture
def blockchain():
    accounts = load_accounts([])
    return Blockchain(TESTS_WORKING_DIR, load_configs(TESTS_WORKING_DIR), accounts)


@pytest.fixture
def create_blockchain():
    def _create_blockchain():
        accounts = load_accounts([])
        return Blockchain(TESTS_WORKING_DIR, load_configs(TESTS_WORKING_DIR), accounts)
    return _create_blockchain


@pytest.fixture
def environ():
    @contextmanager
    def temp_environ():
        prev_environ = {**os.environ}
        with TemporaryDirectory() as tmpdir:
            with chdir(tmpdir):
                yield tmpdir
        os.environ = prev_environ
    return temp_environ