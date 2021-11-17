from pab.contract import ContractManager


def test_contracts_load_from_file(blockchain):
    mgr = ContractManager(blockchain.w3, blockchain.root)
    assert mgr.contracts
    assert "WBTC" in mgr.contracts.keys()

def test_contract_read(blockchain):
    mgr = ContractManager(blockchain.w3, blockchain.root)
    assert mgr.read_contract("WBTC")