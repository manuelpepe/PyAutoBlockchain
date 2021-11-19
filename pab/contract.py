import json
import typing

from pathlib import Path

if typing.TYPE_CHECKING:
    from web3 import Web3

from pab.config import ABIS_DIR, CONTRACTS_FILE


class ContractManager:
    """
    Stores contract definitions (address and location of the abi file).
    Reads and returns contracts from the network.
    """

    def __init__(self, w3: "Web3", root: Path):
        self.w3 = w3
        self.root = root
        self.abisdir = root / ABIS_DIR
        self.contracts = self.load_contracts()
    
    def load_contracts(self):
        with open(self.root / CONTRACTS_FILE, "r") as fp:
            self.contracts = json.load(fp)
        return self.contracts

    def get(self, name: str):
        from web3 import Web3
        if not name in self.contracts.keys():
            raise ValueError("Contract not found.")
        contract = self.contracts[name] 
        with open(self.abisdir / contract["abifile"], "r") as fp:
            return self.w3.eth.contract(
                address=Web3.toChecksumAddress(contract["address"]), 
                abi=fp.read()
            )

