from __future__ import annotations

import json
import logging

from typing import Any, Callable, Optional, List
from pathlib import Path
from datetime import datetime, timedelta

from pab.blockchain import Blockchain
from pab.strategy import BaseStrategy, RescheduleError, SpecificTimeRescheduleError
from pab.config import TASKS_FILE, DATETIME_FORMAT



class Job:
    """ Container for a strategy to be executed in the future """ 
    logger = logging.getLogger("QueuedItem")

    RUN_ASAP = -10
    RUN_NEVER = -20

    def __init__(self, id_: int, strat: BaseStrategy, next_at: int, repeat_every: Optional[dict] = None):
        self.logger = logging.getLogger(f"Queued {strat}") 
        self.id = id_
        self.strategy = strat
        self.next_at = next_at
        self.repeat_every = repeat_every
        self.last_start = 0

    def reschedule(self) -> None:
        """ Calculates next execution from repetition data. """
        next_run = self.next_repetition_time() if self.repeats() else self.RUN_NEVER
        self.schedule_for(next_run)

    def repeats(self) -> bool:
        """ True if Job has repetition data. """
        return bool(self.repeat_every)

    def next_repetition_time(self) -> int:
        last = datetime.fromtimestamp(self.last_start)
        new = last + timedelta(**self.repeat_every)
        return int(new.timestamp())

    def schedule_for(self, next_at: int) -> None:
        if type(next_at) != int:
            raise ValueError("Schedule for must receive an integer timestamp")
        if next_at == self.RUN_NEVER:
            self.logger.warning(f"{self} disabled")
        else:
            timestamp = datetime.fromtimestamp(next_at).strftime(DATETIME_FORMAT)
            self.logger.info(f"Next run of {self} will be at {timestamp}")
        self.next_at = next_at
    
    def is_ready(self) -> bool:
        if self.next_at == self.RUN_ASAP:
            return True
        elif self.next_at == self.RUN_NEVER:
            return False
        elif self.next_at > 0:
            return datetime.fromtimestamp(self.next_at) < datetime.now()
        else:
            raise ValueError(f"Wrong value {self.next_at} of type {type(self.next_at)} for QueuedItem.next_at #{self.id}")

    def process(self) -> None:
        try:
            self._process()
        except SpecificTimeRescheduleError as err:
            self.logger.warning(err)
            self.schedule_for(int(err.next_at))
        except RescheduleError as err:
            self.logger.warning(err)
            self.reschedule()

    def _process(self) -> None:
        if self.is_ready():
            self.logger.info(f"Running task {self.strategy}")
            self.last_start = datetime.now().timestamp()
            self.strategy.run()
            self.reschedule()
            self.logger.info(f"Done with {self.strategy}")

    def __str__(self):
        return f"QueuedItem#{self.id} for {self.strategy}"


class Queue:
    """ Wrapper for a list of Jobs """
    def __init__(self, items: List[Job]):
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
    def __init__(self, blockchain: Blockchain, strategies: list[BaseStrategy]):
        self.blockchain = blockchain
        self.strategies = strategies

    def load(self) -> Queue:
        with open(Path.cwd() / TASKS_FILE, "r") as fp:
            tasks = self._load_tasks_json_or_exception(fp)
            return self._create_queue_from_list(tasks)
        
    def _load_tasks_json_or_exception(self, fhandle) -> List[dict]:
        try:
            data = json.load(fhandle)
            self._validate_raw_data(data)
            return data
        except json.JSONDecodeError as err:
            raise QueueLoadError("Error loading tasks.json") from err

    def _validate_raw_data(self, data: Any) -> None:
        if not isinstance(data, list):
            raise QueueLoadError("Data should be a list of dicts")
        for item in data:
            if not isinstance(item, dict):
                raise QueueLoadError("Data should be a list of dicts")

    def _create_queue_from_list(self, tasks: List[dict]) -> Queue:
        out = []
        for ix, data in enumerate(tasks):
            strat = self._create_strat_from_data(data)
            repeat = data.get("repeat_every", {})
            item = Job(ix, strat, Job.RUN_ASAP, repeat_every=repeat)
            out.append(item)
        return Queue(out)

    def _create_strat_from_data(self, data: dict) -> BaseStrategy:
        strat_class = self._find_strat_by_name(data["strategy"])
        return strat_class(self.blockchain, data["name"], **data.get("params", {}))

    def _find_strat_by_name(self, name: str) -> Callable | None:
        for class_ in self.strategies:
            if class_.__name__ == name:
                return class_
        raise UnkownStrategyError(f"Can't find strategy '{name}'")


class QueueLoadError(Exception):
    pass


class QueuedItemNotReady(Exception):
    pass


class UnkownStrategyError(Exception): 
    pass