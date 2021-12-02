import sys
import logging
import importlib

from pathlib import Path
from eth_account.account import Account

from pab.blockchain import Blockchain


__all__ = [
    "BaseStrategy",
    "PABError",
    "RescheduleError",
    "SpecificTimeRescheduleError",
    "import_strategies",
]


def load_strategies(root: Path) -> list['BaseStrategy']:
    import_strategies(root)
    return BaseStrategy.__subclasses__()


def import_strategies(root: Path):
    try:
        path = str(root)
        sys.path.append(path)
        importlib.import_module("strategies")
        sys.path.remove(path)
    except ModuleNotFoundError as err:
        raise RuntimeError("Can't find any strategies. Create a 'strategies' module in your CWD.") from err


class BaseStrategy:
    """ Base class for strategies """
    def __init__(self, blockchain: Blockchain, name: str):
        self.logger = logging.getLogger(f"{self.__class__.__name__}-{name}")
        self.blockchain = blockchain
        self.name = name

    @property
    def accounts(self):
        return self.blockchain.accounts

    @property
    def contracts(self):
        return self.blockchain.contracts

    def run(self):
        raise NotImplementedError("Childs of BaseStrategy must implement 'run'")

    def transact(self, account: Account, func: callable, args: tuple):
        res = self.blockchain.transact(account, func, args)
        return res
    
    def __str__(self):
        return f"{self.name} on {self.blockchain}"


class PABError(Exception):
    """ Base class for errors while running tasks. 
    Unhandleded PABErrors will prevent further excecutions of a strategy. """
    pass


class RescheduleError(PABError):
    """ Strategies can raise this exception to tell PAB to optionally reschedule them in known scenarios. """
    pass


class SpecificTimeRescheduleError(RescheduleError):
    """ Same as `RescheduleError` but with specific a specific date and time. """
    def __init__(self, message, next_at = None):
        super().__init__(message)
        self.next_at = next_at