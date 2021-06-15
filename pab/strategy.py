import json
import time
import logging

from datetime import datetime, timedelta
from pathlib import Path
from typing import List

from pab.blockchain import Blockchain
from pab.config import DATETIME_FORMAT
from pab.utils import *


__all__ = [
    "BaseStrategy",
    "PABError",
    "RescheduleError",
    "SpecificTimeRescheduleError",
]


class BaseStrategy:
    """ Base class for strategies """
    def __init__(self, blockchain: Blockchain, name: str):
        self.logger = logging.getLogger(f"{self.__class__.__name__}-{name}")
        self.blockchain = blockchain
        self.name = name

    def run(self):
        raise NotImplementedError("Childs of BaseStrategy must implement 'run'")

    def _transact(self, func: callable, args: tuple):
        res = self.blockchain.transact(func, args)
        time.sleep(2)
    
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