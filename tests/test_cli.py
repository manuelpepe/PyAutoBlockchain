import json

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from eth_account.account import Account
from pab.cli import main, parser


def test_create_parser():
    p = parser()
    assert p


def test_create_keyfile():
    filepass = "MYPASS"
    inputs = ["0x00f02cb8ad2ab4bdd67a59d50535f431d2c89d42144c3ed2fe06c79617ea3a86", filepass, filepass]
    with patch('getpass.getpass', new=lambda x: inputs.pop(0)), \
         TemporaryDirectory() as tmpdir:
        keyfile = Path(tmpdir) / 'keyfile'
        main(['create-keyfile', '-o', str(keyfile)])
        assert keyfile.is_file()
        with keyfile.open('r') as fp:
            assert Account.decrypt(json.load(fp), filepass)