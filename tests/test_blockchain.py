import os
import web3
import tempfile

from unittest.mock import MagicMock

from pab.blockchain import Blockchain


def test_w3_connection(blockchain: Blockchain):
    assert isinstance(blockchain.w3, web3.Web3)
    assert blockchain.wallet is None and blockchain.owner is None


def test_load_wallet(blockchain: Blockchain):
    blockchain.w3.eth.account.decrypt = MagicMock(name="decrypt")
    with tempfile.NamedTemporaryFile("w") as keyfile:
        os.environ["POLYCOMP_KEY"] = "test"
        blockchain.load_wallet("0x12345", keyfile.name)
        blockchain.w3.eth.account.decrypt.assert_called_once()


def test_load_wallet_updates_txn_handler(blockchain: Blockchain):
    blockchain.w3.eth.account.decrypt = MagicMock(name="decrypt")
    blockchain.w3.eth.account.decrypt.return_value = {}
    my_address = "0x12345"
    with tempfile.NamedTemporaryFile("w") as keyfile:
        os.environ["POLYCOMP_KEY"] = "test"
        blockchain.load_wallet(my_address, keyfile.name)
        assert blockchain.owner == my_address
        assert blockchain.txn_handler.owner == my_address
