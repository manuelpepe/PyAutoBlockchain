import logging

from pathlib import Path
from typing import Dict

from pab.contract import ContractManager
from pab.transaction import TransactionHandler
from pab.config import Config
from eth_account.account import Account


_logger = logging.getLogger("pab.blockchain")


class Blockchain:
    """ API for contracts and transactions """

    def __init__(self, root: Path, config: Config, accounts: Dict[int, Account]):
        self.root = root
        self.config = config
        self.rpc = config.get('endpoint')
        self.id = config.get('chainId')
        self.name = config.get('blockchain')
        self.w3 = self._connect_web3()
        self.accounts = accounts
        self.contracts = ContractManager(self.w3, root)
        self._txn_handler = TransactionHandler(self.w3, self.id, config)

    def _connect_web3(self):
        from web3 import Web3
        from web3.middleware.geth_poa import geth_poa_middleware
        w3 = Web3(Web3.HTTPProvider(self.rpc))
        w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        return w3

    def transact(self, account: Account, func: callable, args: tuple):
        return self._txn_handler.transact(account, func, args)

    def __str__(self):
        return f"{self.name}#{self.id}"
