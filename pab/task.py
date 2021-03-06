from __future__ import annotations

import json
import logging

from typing import Any, List, NewType, TextIO
from pathlib import Path
from datetime import datetime, timedelta

from pab.blockchain import Blockchain
from pab.strategy import (
    BaseStrategy,
    RescheduleError,
    SpecificTimeRescheduleError,
    StrategiesDict,
)
from pab.config import TASKS_FILE, DATETIME_FORMAT


TaskList = NewType("TaskList", list["Task"])
""" Type for an explicit list of Tasks. """

RawTasksData = NewType("RawTasksData", List[dict])
""" Type for an explicit list of task data dictionaries.  """


class Task:
    """Container for a strategy to be executed in the future"""

    RUN_ASAP: int = -10
    """ Constant. Means job should be rescheduled to run ASAP. """
    RUN_NEVER: int = -20
    """ Constant. Means job should't be rescheduled. """

    def __init__(
        self,
        id_: int,
        strat: BaseStrategy,
        next_at: int,
        repeat_every: dict | None = None,
    ):
        self.id = id_
        """ Internal Task ID """
        self.strategy: BaseStrategy = strat
        """ Strategy object """
        self.next_at: int = next_at
        """ Next execution time as timestamp"""
        self.repeat_every: dict[str, int] | None = repeat_every
        """ Repetition data. A dict that functions as kwargs for `datetime.timedelta` """
        self.last_start: int = 0
        """ Last execution start time as timestamp"""
        self.logger = logging.getLogger(f"{self}")

    def reschedule(self) -> None:
        """Calculates next execution if applies and calls :meth:`schedule_for`"""
        next_run = self.next_repetition_time() if self.repeats() else self.RUN_NEVER
        self.schedule_for(next_run)

    def repeats(self) -> bool:
        """True if Task has repetition data."""
        return bool(self.repeat_every)

    def next_repetition_time(self) -> int:
        """Returns next repetition time based on :attr:`last_start` and :attr:`repeat_every`."""
        if not self.repeat_every:
            raise RuntimeError(
                f"Can't calculate repetition time for {self} without repetition data."
            )
        last = datetime.fromtimestamp(self.last_start)
        new = last + timedelta(**self.repeat_every)
        return int(new.timestamp())

    def schedule_for(self, next_at: int) -> None:
        """Updates :attr:`self.next_at` for a specific time. Will disable job if value is
        :attr:`Task.RUN_NEVER`."""
        if type(next_at) != int:
            raise ValueError("Schedule for must receive an integer timestamp")
        if next_at == self.RUN_NEVER:
            self.logger.warning(f"{self} disabled")
        else:
            timestamp = datetime.fromtimestamp(next_at).strftime(DATETIME_FORMAT)
            self.logger.info(f"Next run of {self} will be at {timestamp}")
        self.next_at = next_at

    def is_ready(self) -> bool:
        """Returns True if job is ready to run based on :attr:`next_at`."""
        if self.next_at == self.RUN_ASAP:
            return True
        elif self.next_at == self.RUN_NEVER:
            return False
        elif self.next_at > 0:
            return datetime.fromtimestamp(self.next_at) < datetime.now()
        else:
            raise ValueError(
                f"Wrong value {self.next_at} of type {type(self.next_at)} for {self}"
            )

    def process(self) -> None:
        """Calls :meth:`_process` and handles :exc:`pab.strategy.RescheduleError`."""
        try:
            self._process()
        except SpecificTimeRescheduleError as err:
            self.logger.warning(err)
            self.schedule_for(int(err.next_at))
        except RescheduleError as err:
            self.logger.warning(err)
            self.reschedule()

    def _process(self) -> None:
        """Runs strategy and updates schedule."""
        if self.is_ready():
            self.logger.info(f"Running task {self.strategy}")
            self.last_start = int(datetime.now().timestamp())
            self.strategy.run()
            self.reschedule()
            self.logger.info(f"Done with {self.strategy}")

    def __str__(self):
        return f"Task[{self.strategy}]"


class TaskFileParser:
    """Parses a tasks file and loads a TaskList."""

    REQUIRED_TASK_FIELDS: list[str] = ["name", "strategy"]
    """ Fields that must be declared in all tasks. """

    def __init__(self, root: Path, blockchain: Blockchain, strategies: StrategiesDict):
        self.root: Path = root
        """ Root of the project. """
        self.blockchain: Blockchain = blockchain
        """ :class:`Blockchain` used by tasks. """
        self.strategies: StrategiesDict = strategies
        """ Strategies dictionary. """

    def load(self) -> TaskList:
        """Loads TaskList from tasks file."""
        with open(self.root / TASKS_FILE) as fp:
            tasks = self._load_tasks_json_or_exception(fp)
            return self._create_tasklist(tasks)

    def _load_tasks_json_or_exception(self, fhandle: TextIO) -> RawTasksData:
        """Parses TextIO input as JSON, validates and returns raw data.
        May raise :exc:`TasksFileParseError`."""
        try:
            data = json.load(fhandle)
            self._validate_raw_data(data)
            return RawTasksData(data)
        except json.JSONDecodeError as err:
            raise TasksFileParseError("Error parsing tasks.json as JSON") from err

    def _validate_raw_data(self, data: Any) -> None:
        """Validates raw tasks data format. May raise :exc:`TasksFileParseError`."""
        if not isinstance(data, list):
            raise TasksFileParseError("tasks.json must be a list of dicts")
        for task in data:
            if not isinstance(task, dict):
                raise TasksFileParseError("All tasks in tasks.json must dicts")
            if not all(field in task.keys() for field in self.REQUIRED_TASK_FIELDS):
                fields = ", ".join(self.REQUIRED_TASK_FIELDS)
                raise TasksFileParseError(
                    f"All tasks must declare all the following fields: {fields}"
                )

    def _create_tasklist(self, tasks: RawTasksData) -> TaskList:
        """Creates a list of :class:`Task` objects from raw data. May raise :exc:`TaskLoadError`."""
        out = []
        for ix, data in enumerate(tasks):
            strat = self._create_strat_from_data(data)
            repeat = data.get("repeat_every", {})
            item = Task(ix, strat, Task.RUN_ASAP, repeat_every=repeat)
            out.append(item)
        return TaskList(out)

    def _create_strat_from_data(self, data: dict) -> BaseStrategy:
        """Creates a single :class:`Task` object from raw data. May raise :exc:`TaskLoadError`."""
        strat_class = self._find_strat_by_name(data["strategy"])
        try:
            return strat_class(self.blockchain, data["name"], **data.get("params", {}))
        except TypeError as err:
            msg = f"Error loading task '{data['name']}': {err}"
            raise TaskLoadError(msg)

    def _find_strat_by_name(self, name: str) -> type[BaseStrategy]:
        """Finds a strategy by name. May raise :exc:`UnkownStrategyError`."""
        if name in self.strategies.keys():
            return self.strategies[name]
        raise UnkownStrategyError(f"Can't find strategy '{name}'")


class TasksFileParseError(Exception):
    """Error while parsing tasks.json"""

    pass


class TaskLoadError(Exception):
    """Error while loading a task"""

    pass


class UnkownStrategyError(TaskLoadError):
    """A strategy required by a task could not be found."""

    pass
