from __future__ import annotations

import sys
import logging
import importlib

from pathlib import Path
from typing import Dict, TYPE_CHECKING
from abc import ABC, abstractmethod


if TYPE_CHECKING:
    from eth_account.account import LocalAccount
    from web3.types import TxReceipt
    from pab.contract import ContractManager

from pab.blockchain import Blockchain


__all__ = [
    "import_strategies",
    "BaseStrategy",
    "PABError",
    "RescheduleError",
    "SpecificTimeRescheduleError",
    "load_strategies",
]


_STRATS_MODULE_NAME = "strategies"


def load_strategies(root: Path) -> list['BaseStrategy']:
    import_strategies(root)
    return BaseStrategy.__subclasses__()


def import_strategies(root: Path):
    """ Imports `strategies` module from `root` directory. """
    if not root.is_dir():
        raise FileNotFoundError(f"Directory {root} not found")
    try:
        path = str(root)
        if _STRATS_MODULE_NAME in sys.modules.keys():
            # If a _STRATS_MODULE_NAME module is already loaded we remove it
            # to avoid python reusing it https://docs.python.org/3/library/sys.html#sys.modules
            del sys.modules[_STRATS_MODULE_NAME]
        sys.path.insert(0, path)
        importlib.import_module(_STRATS_MODULE_NAME)
        removed = sys.path.pop(0)
        if removed != path:
            raise RuntimeError("Unexpected value removed from sys.path")
    except ModuleNotFoundError as err:
        raise RuntimeError(f"Can't find any strategies. Create a '{_STRATS_MODULE_NAME}' module in your CWD.") from err


class BaseStrategy(ABC):
    """ Abstract Base Class for custom strategies. """
    def __init__(self, blockchain: Blockchain, name: str):
        self.logger = logging.getLogger(f"{self.__class__.__name__}-{name}")
        self.blockchain: Blockchain = blockchain
        """ Current blockchain connection. """
        self.name: str = name

    @property
    def accounts(self) -> Dict[int, 'LocalAccount']:
        """ Returns available accounts in current blockchain. 
        You can access specific accounts with numeric indexes"""
        return self.blockchain.accounts

    @property
    def contracts(self) -> 'ContractManager':
        """ Returns a :ref:`pab.contract.ContractManager`. You can use `self.contracts.get(name)`
        to retrieve a contract by name. """
        return self.blockchain.contracts

    @abstractmethod
    def run(self):
        """ Strategy entrypoint. Must be defined by all childs. """
        raise NotImplementedError("Childs of BaseStrategy must implement 'run'")

    def transact(self, account: 'LocalAccount', func: callable, args: tuple) -> "TxReceipt":
        """ Makes a transaction on the current blockchain. """
        return self.blockchain.transact(account, func, args)
    
    def __str__(self):
        return f"{self.name}"


class PABError(Exception):
    """ Base class for errors while running tasks. 
    Unhandleded PABErrors will prevent further excecutions of a strategy. """
    pass


class RescheduleError(PABError):
    """ Strategies can raise this exception to tell PAB to reschedule them in known scenarios. """
    pass


class SpecificTimeRescheduleError(RescheduleError):
    """ Same as `RescheduleError` but at a specific time passed as a timestamp. """
    def __init__(self, message: str, next_at: int = None):
        super().__init__(message)
        self.next_at = next_at