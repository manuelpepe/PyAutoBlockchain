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
    "CompoundStrategy",
    "CompoundError",
    "RescheduleError",
    "SpecificTimeRescheduleError",
]


class CompoundStrategy:
    """ Base class for compound strategies """
    def __init__(self, blockchain: Blockchain, name: str):
        self.logger = logging.getLogger(f"{self.__class__.__name__}-{name}")
        self.blockchain = blockchain
        self.name = name

    def compound(self):
        raise NotImplementedError("Childs of CompoundStrategy must implement 'compound'")

    def _transact(self, func: callable, args: tuple):
        res = self.blockchain.transact(func, args)
        time.sleep(2)
    
    def __str__(self):
        return f"{self.name} on {self.blockchain}"


class CompoundError(Exception):
    """ Base class for errors while compounding. 
    Unhandleded CompoundErrors will prevent further excecutions of a strategy. """
    pass


class RescheduleError(CompoundError):
    """ Strategies can raise this exception to tell the compounder to optionally reschedule them in known scenarios. """
    pass


class SpecificTimeRescheduleError(RescheduleError):
    """ Same as `RescheduleError` but with specific a specific date and time. """
    def __init__(self, message, next_at = None):
        super().__init__(message)
        self.next_at = next_at