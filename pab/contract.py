import json

from pathlib import Path
from typing import Dict, TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from web3 import Web3
    from web3.contract import Contract

from pab.config import ABIS_DIR, CONTRACTS_FILE


@dataclass
class ContractData:
    """Stores smart contract data"""

    name: str
    address: str
    abi: str


class ContractManager:
    """
    Stores contract definitions (address and location of the abi file).
    Reads and returns contracts from the network.
    """

    def __init__(self, w3: "Web3", root: Path):
        self.w3: "Web3" = w3
        self.root: Path = root
        self.abisdir: Path = root / ABIS_DIR
        self.contracts: Dict[str, "ContractData"] = self._load_contracts()

    def _load_contracts(self) -> Dict[str, "ContractData"]:
        """Reads and parses `contracts.json`."""
        with open(self.root / CONTRACTS_FILE) as fp:
            contracts = json.load(fp)
            if not isinstance(contracts, dict):
                raise ContractDefinitionError("Data in contracts.json is not a dict")
            for _name, data in contracts.items():
                self._check_valid_contract_data(data)
                self._check_abifile_exists(data["abifile"])
        return self._parse_contract_data(contracts)

    def _parse_contract_data(
        self, contracts_data: dict[str, dict]
    ) -> Dict[str, "ContractData"]:
        """Replaces the raw contract data from `contracts.json` with the :class:`ContractData` dataclass."""
        contracts = {}
        for name, data in contracts_data.items():
            abifile = Path(self.abisdir, data["abifile"])
            abi = abifile.read_text()
            contracts[name] = ContractData(name, data["address"], abi)
        return contracts

    def _check_valid_contract_data(self, data: dict) -> None:
        """Validates that the data loaded from `contracts.json` is valid."""
        if not isinstance(data, dict):
            raise ContractDefinitionError(
                "Contract data must be a dict with address and abifile."
            )
        req_fields = {"address", "abifile"}
        if set(data.keys()) != req_fields:
            raise ContractDefinitionError(
                "Contract data must be a dict with only 'address' and 'abifile' values."
            )

    def _check_abifile_exists(self, abifile) -> None:
        """Validates that all abifiles defined in `contracts.json` exist."""
        filepath = Path(self.abisdir / abifile)
        if not filepath.is_file():
            raise ContractDefinitionError(f"ABI file at abis/{abifile} not found.")

    def get(self, name: str) -> "Contract":
        """Returns contract by name. Contract must be defined in `CONTRACTS_FILE` and `ABIS_DIR`."""
        from web3 import Web3

        if name not in self.contracts.keys():
            raise ValueError(f"Contract '{name}' not found.")
        contract = self.contracts[name]
        return self.w3.eth.contract(
            address=Web3.toChecksumAddress(contract.address), abi=contract.abi
        )


class ContractDefinitionError(Exception):
    ...
