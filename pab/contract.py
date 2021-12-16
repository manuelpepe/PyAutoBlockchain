import json
import typing

from pathlib import Path

if typing.TYPE_CHECKING:
    from web3 import Web3
    from web3.contract import Contract

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
        self.contracts = self._load_contracts()
    
    def _load_contracts(self) -> list['Contract']:
        """ Reads `contracts.json` and checks format. """
        with open(self.root / CONTRACTS_FILE, "r") as fp:
            contracts = json.load(fp)
            if not isinstance(contracts, dict):
                raise ContractDefinitionError("Data in contracts.json is not a dict")
            for name, data in contracts.items():
                self._check_valid_contract_data(data)
                self._check_abifile_exists(data['abifile'])
        return contracts
    
    def _check_valid_contract_data(self, data: dict):
        if not isinstance(data, dict):
            raise ContractDefinitionError("Contract data must be a dict with address and abifile.")
        req_fields = ['address', 'abifile']
        for attr in req_fields:
            if not attr in data.keys():
                raise ContractDefinitionError("Contract data must be a dict with address and abifile.")

    def _check_abifile_exists(self, abifile):
        filepath = Path(self.abisdir / abifile)
        if not filepath.is_file():
            raise ContractDefinitionError(f"ABI file at abis/{abifile} not found.")

    def get(self, name: str) -> 'Contract':
        from web3 import Web3
        if not name in self.contracts.keys():
            raise ValueError("Contract not found.")
        contract = self.contracts[name] 
        with open(self.abisdir / contract["abifile"], "r") as fp:
            return self.w3.eth.contract(
                address=Web3.toChecksumAddress(contract["address"]), 
                abi=fp.read()
            )


class ContractDefinitionError(Exception):
    ...