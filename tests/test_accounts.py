from contextlib import contextmanager
import os

from tempfile import TemporaryDirectory
from pathlib import Path
from unittest.mock import patch

from eth_account.signers.local import LocalAccount
from hexbytes.main import HexBytes

from pab.accounts import create_keyfile, load_accounts


@contextmanager
def env_account(ix, pk):
    name = f"PAB_PK{ix}"
    try:
        os.environ[name] = pk
        yield
    finally:
        del os.environ[name]


def test_load_wallet_from_environ():
    key = "0x00f02cb8ad2ab4bdd67a59d50535f431d2c89d42144c3ed2fe06c79617ea3a86"
    with env_account(1, key):
        address = "0xE52801D8B3fac17952AcA224ECb195aF5e7922a2"
        os.environ["PAB_PK1"] = key
        accounts = load_accounts([])
        assert len(accounts) == 1
        assert accounts[1].address == address
        assert accounts[1].key == HexBytes(key)
        assert isinstance(accounts[1], LocalAccount)


def test_load_accounts_from_keyfile():
    filepass = "MYPASS"
    pk = "0x00f02cb8ad2ab4bdd67a59d50535f431d2c89d42144c3ed2fe06c79617ea3a86"
    with patch(
        "getpass.getpass", new=lambda x: filepass
    ), TemporaryDirectory() as tmpdir:
        keyfile = Path(tmpdir) / "keyfile"
        create_keyfile(keyfile, pk, filepass)
        assert keyfile.is_file()
        accs = load_accounts([keyfile])
        assert len(accs) == 1
        assert accs[0].key == HexBytes(pk)
        assert accs[0].address == "0xE52801D8B3fac17952AcA224ECb195aF5e7922a2"
        assert isinstance(accs[0], LocalAccount)
