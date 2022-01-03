from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from hexbytes.main import HexBytes
from pab.accounts import load_accounts
from pab.cli import main, parser


def test_create_parser():
    p = parser()
    assert p


def test_create_keyfile():
    filepass = "MYPASS"
    pk = "0x00f02cb8ad2ab4bdd67a59d50535f431d2c89d42144c3ed2fe06c79617ea3a86"
    inputs = [pk, filepass, filepass, filepass]
    with patch(
        "getpass.getpass", new=lambda x: inputs.pop(0)
    ), TemporaryDirectory() as tmpdir:
        keyfile = Path(tmpdir) / "keyfile"
        main(["create-keyfile", "-o", str(keyfile)])
        assert keyfile.is_file()
        accs = load_accounts([keyfile])
        assert len(accs) == 1
        assert accs[0].key == HexBytes(pk)
