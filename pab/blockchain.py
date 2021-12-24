import logging

from pathlib import Path
from typing import Dict, TYPE_CHECKING


from pab.contract import ContractManager
from pab.transaction import TransactionHandler
from pab.config import Config

if TYPE_CHECKING:
    from web3 import Web3
    from web3.types import TxReceipt
    from eth_account.account import LocalAccount


class Blockchain:
    """ Web3 connection manager. """

    def __init__(self, root: Path, config: Config, accounts: Dict[int, 'LocalAccount']):
        self.root = root
        self.config = config
        self.rpc: str = config.get('endpoint')
        """ Network RPC URL """
        self.id: int = config.get('chainId')
        """ Network Chain ID """
        self.name: str = config.get('blockchain')
        """ Network name """
        self.w3: "Web3" = self._connect_web3()
        """ Internal Web3 connection"""
        self.accounts: Dict[int, 'LocalAccount'] = accounts
        """ List of loaded accounts """
        self.contracts: ContractManager = ContractManager(self.w3, root)
        """ Initialized contract manager """
        self._txn_handler = TransactionHandler(self.w3, self.id, config)
        """ Initialized transaction handler"""

    def _connect_web3(self):
        from web3 import Web3
        from web3.middleware.geth_poa import geth_poa_middleware
        w3 = Web3(Web3.HTTPProvider(self.rpc))
        w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        return w3

    def transact(self, account: 'LocalAccount', func: callable, args: tuple) -> "TxReceipt":
        """ Uses internal transaction handler to submit a transaction. """
        return self._txn_handler.transact(account, func, args)

    def __str__(self):
        return f"{self.name}#{self.id}"
