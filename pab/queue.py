import sys
import json
import logging
import importlib

from contextlib import contextmanager
from typing import Optional, List
from pathlib import Path
from datetime import datetime, timedelta

from pab.blockchain import Blockchain
from pab.strategy import BaseStrategy
from pab.config import TASKS_FILE, DATETIME_FORMAT


class QueueItem:
    """ Container for a strategy to be executed in the future """ 
    logger = logging.getLogger("QueuedItem")

    RUN_ASAP = -10
    RUN_NEVER = -20

    def __init__(self, id_: int, strat: BaseStrategy, next_at: int, repeat_every: Optional[dict] = None):
        self.id = id_
        self.strategy = strat
        self.next_at = next_at
        self.repeat_every = repeat_every
        self.last_start = 0

    def reschedule(self):
        next_run = self.next_repetition_time() if self.repeats() else self.RUN_NEVER
        self.schedule_for(next_run)

    def repeats(self):
        return bool(self.repeat_every)

    def next_repetition_time(self):
        last = datetime.fromtimestamp(self.last_start)
        new = last + timedelta(**self.repeat_every)
        return int(new.timestamp())

    def schedule_for(self, next_at: int):
        if type(next_at) != int:
            raise ValueError("Schedule for must receive an integer timestamp")
        if next_at == self.RUN_NEVER:
            self.logger.warning(f"{self} disabled")
        else:
            timestamp = datetime.fromtimestamp(next_at).strftime(DATETIME_FORMAT)
            self.logger.info(f"Next run of {self} will be at {timestamp}")
        self.next_at = next_at
    
    def is_ready(self):
        if self.next_at == self.RUN_ASAP:
            return True
        elif self.next_at == self.RUN_NEVER:
            return False
        elif self.next_at > 0:
            return datetime.fromtimestamp(self.next_at) < datetime.now()
        else:
            raise ValueError(f"Wrong value {self.next_at} of type {type(self.next_at)} for QueuedItem.next_at #{self.id}")

    def process(self):
        if self.is_ready():
            self.logger.info(f"Running task {self.strategy}")
            self.last_start = datetime.now().timestamp()
            self.strategy.run()
            self.reschedule()
            self.logger.info(f"Done with {self.strategy}")

    def __str__(self):
        return f"QueuedItem#{self.id} for {self.strategy}"


class Queue:
    """ Wrapper for a list of QueueItems """
    def __init__(self, items: List[QueueItem]):
        self.items = items

    def __getitem__(self, key):
        return self.items[key]

    def __iter__(self):
        return self.items.__iter__()
    
    def __next__(self):
        return self.items.__next__()

    def __len__(self):
        return len(self.items)


class QueueLoader:
    """ Loads a Queue from raw data """
    def __init__(self, blockchain: Blockchain = None, import_local_strategies: bool = True):
        self.blockchain = blockchain
        self.imported_module = None
        if import_local_strategies:
            self.import_local_strategies()
    
    def import_local_strategies(self):
        if not self.imported_module:
            try:
                with self._add_cwd_to_path():
                    self.imported_module = importlib.import_module("strategies")
            except ModuleNotFoundError as err:
                raise RuntimeError("Can't find any strategies. Create a 'strategies' module in your CWD.") from err
    
    @contextmanager
    def _add_cwd_to_path(self):
        path = str(Path.cwd())
        sys.path.append(path)
        yield
        sys.path.remove(path)

    def load(self):
        with open(Path.cwd() / TASKS_FILE, "r") as fp:
            tasks = self._load_tasks_json_or_exception(fp)
            return self._create_queue_from_list(tasks)
        
    def _load_tasks_json_or_exception(self, fhandle):
        try:
            return json.load(fhandle)
        except json.JSONDecodeError as err:
            raise QueueLoadError("Error loading tasks.json") from err

    def _create_queue_from_list(self, tasks: List[dict]):
        out = []
        for ix, data in enumerate(tasks):
            strat = self._create_strat_from_data(data)
            repeat = data.get("repeat_every", {})
            item = QueueItem(ix, strat, QueueItem.RUN_ASAP, repeat_every=repeat)
            out.append(item)
        return Queue(out)

    def _create_strat_from_data(self, data: dict) -> BaseStrategy:
        strat_class = self._find_strat_by_name(data["strategy"])
        return strat_class(self.blockchain, data["name"], **data.get("params", {}))

    def _find_strat_by_name(self, name: str):
        for class_ in BaseStrategy.__subclasses__():
            if class_.__name__ == name:
                return class_
        raise UnkownStrategyError(f"Can't find strategy '{name}'")

    @classmethod
    def list_strats(cls):
        return BaseStrategy.__subclasses__()


class QueueLoadError(Exception):
    pass


class QueuedItemNotReady(Exception):
    pass


class UnkownStrategyError(Exception): 
    pass