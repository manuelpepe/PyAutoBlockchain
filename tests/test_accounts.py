import os

from hexbytes.main import HexBytes


def test_load_wallet(create_blockchain, environ):
    with environ():
        address = "0xE52801D8B3fac17952AcA224ECb195aF5e7922a2"
        key = "0x00f02cb8ad2ab4bdd67a59d50535f431d2c89d42144c3ed2fe06c79617ea3a86"
        os.environ["PAB_PK1"] = key
        blockchain = create_blockchain()
        assert len(blockchain.accounts) == 1
        assert blockchain.accounts[1].address == address
        assert blockchain.accounts[1].key == HexBytes(key)
