import os
import getpass
import logging

from os.path import isfile
from typing import Optional

from web3 import Web3
from web3.middleware.geth_poa import geth_poa_middleware

from pab.contract import ContractManager
from pab.transaction import TransactionHandler
from pab.config import KEY_FILE


_logger = logging.getLogger("pab.blockchain")


def load_wallet(w3: Web3, keyfile: Optional[str]):
    if keyfile is None:
        keyfile = KEY_FILE
    if not isfile(keyfile):
        _logger.warning(f"Keyfile at '{keyfile}' not found. Loading without wallet.")
        return
    with open(keyfile) as fp:
        wallet_pass = os.environ.get("POLYCOMP_KEY")
        if not wallet_pass:
            wallet_pass = getpass.getpass("Enter wallet password: ")
        return w3.eth.account.decrypt(fp.read(), wallet_pass)

class Blockchain:
    """ API for contracts and transactions """

    def __init__(self, rpc: str, id_: int, name: str, txn_handler_class: TransactionHandler = TransactionHandler):
        self.rpc = rpc
        self.id = id_
        self.name = name
        self.w3 = self._connect_web3()
        self.txn_handler = txn_handler_class(self.w3, self.id)
        self.contract_manager = ContractManager(self.w3)
        self.wallet = None
        self.owner = None

    def _connect_web3(self):
        w3 = Web3(Web3.HTTPProvider(self.rpc))
        w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        return w3

    def load_wallet(self, owner: str, keyfile: str):
        if self.wallet:
            raise Exception("Wallet already loaded")
        self.wallet = load_wallet(self.w3, keyfile)
        self.owner = owner
        self.update_txn_handler()

    def update_txn_handler(self):
        if self.txn_handler:
            self.txn_handler.private_key = self.wallet
            self.txn_handler.owner = self.owner

    def transact(self, func: callable, args: tuple):
        return self.txn_handler.transact(func, args)

    def read_contract(self, name):
        return self.contract_manager.read_contract(name)

    def __str__(self):
        return f"{self.name}#{self.id}"
