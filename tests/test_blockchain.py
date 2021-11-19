import web3

from pab.blockchain import Blockchain


def test_w3_connection(blockchain: Blockchain):
    assert isinstance(blockchain.w3, web3.Web3)

