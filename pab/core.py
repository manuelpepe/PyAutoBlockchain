from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

import time
import logging
import argparse

from inspect import signature, Parameter
from pathlib import Path
from types import MappingProxyType
from typing import Any, Callable

from pab.accounts import load_accounts

from pab.blockchain import Blockchain
from pab.config import load_configs
from pab.strategy import BaseStrategy, load_strategies
from pab.alert import alert_exception
from pab.task import Task, TaskFileParser, TaskList


class PAB:
    """Loads PAB project from a given path, including configs from
    all sources, strategies from the `strategies` module, and accounts."""

    def __init__(
        self,
        root: Path,
        keyfiles: list[Path] | None = None,
        envs: list[str] | None = None,
    ):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.root = root
        self.config = load_configs(root, envs)
        self.strategies = load_strategies(root)
        self.accounts = load_accounts(keyfiles or [])
        self.blockchain = Blockchain(self.root, self.config, self.accounts)


class Runner(ABC):
    """Base class for PAB Runners.

    Runners execute PAB strategies in different manners.
    All runners must implement ``run``."""

    def __init__(self, pab: PAB):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.pab = pab

    @abstractmethod
    def run(self):
        """Main run method."""
        ...


class TasksRunner(Runner):
    """Loads and runs tasks from `tasks.json`."""

    # TODO: Move to config
    ITERATION_SLEEP = 60

    def __init__(self, *args):
        super().__init__(*args)
        self.tasks: TaskList | list = TaskFileParser(
            self.pab.root, self.pab.blockchain, self.pab.strategies
        ).load()

    def run(self):
        while True:
            self.process_tasks()
            self.logger.debug("Tasks iteration finished.")
            self._sleep()

    def process_tasks(self):
        for item in self.tasks:
            self.process_item(item)

    def process_item(self, item: Task):
        try:
            item.process()
        except Exception as err:
            self.logger.exception(err)
            alert_exception(err, self.pab.config)
            raise err

    def _sleep(self):
        self.logger.debug(f"Sleeping for {self.ITERATION_SLEEP} seconds.")
        time.sleep(self.ITERATION_SLEEP)


@dataclass(frozen=True, eq=True)
class StratParam:
    name: str
    type: Callable | str = field(hash=False)
    default: Any = field(hash=False)


class SingleStrategyRunner(Runner):
    """Runs a single strategy, one time, with custom parameters."""

    TYPES = {"str": str, "int": int, "float": float}

    def __init__(self, *args, strategy: str, params: list[str]):
        super().__init__(*args)
        self._rawparams = params
        strat_class = self.pab.strategies[strategy]
        if not strat_class:
            raise RuntimeError(f"Strategy '{strategy}' not found.")
        self._base_params: list[str] = self._get_base_params()
        self.params: argparse.Namespace = self._parse_params(strat_class)
        self.strat = strat_class(
            self.pab.blockchain, strat_class.__name__, **self.params.__dict__
        )

    def run(self):
        self.strat.run()

    def _parse_params(self, strat_class: type[BaseStrategy]) -> argparse.Namespace:
        parser = self._get_strat_parser(strat_class)
        return parser.parse_args(self._rawparams)

    def _get_strat_parser(
        self, strat_class: type[BaseStrategy]
    ) -> argparse.ArgumentParser:
        """Builds an ArgumentParser from the signature of the current strategy __init__ method."""
        parser = argparse.ArgumentParser(strat_class.__name__, strat_class.__doc__)
        params = self._get_strat_params(strat_class)
        for param in params:
            type_ = self._validate_and_get_param_type(param)
            if param.default is Parameter.empty:
                parser.add_argument(f"--{param.name}", type=type_, required=True)
            else:
                parser.add_argument(
                    f"--{param.name}",
                    type=type_,
                    default=param.default,
                    required=True,
                )
        return parser

    def _validate_and_get_param_type(self, param: StratParam) -> Callable:
        if callable(param.type):
            return param.type
        if param.type in self.TYPES.keys():
            return self.TYPES[param.type]
        raise RuntimeError(
            f"Invalid annotation '{param.type}' for parameter '{param.name}'."
        )

    def _get_strat_params(self, strat) -> set[StratParam]:
        """Recursively retrieve a list of all keyword parameters
        for a strategy constructor."""
        params: MappingProxyType[str, Parameter] = signature(strat).parameters
        all_params: list[StratParam] = []
        for p in params.values():
            # Avoid requesting input for base params that
            # will be passed by the framework
            if (
                p.kind in [Parameter.POSITIONAL_OR_KEYWORD, Parameter.KEYWORD_ONLY]
                and p.name not in self._base_params
            ):
                parsed = StratParam(p.name, p.annotation, p.default)
                all_params.append(parsed)
        for parent in strat.__bases__:
            if parent is not BaseStrategy:
                all_params.extend(self._get_strat_params(parent))
        return set(all_params)

    def _get_base_params(self) -> list[str]:
        """Returns the names of the base parameters of :class:`BaseStrategy`."""
        params = signature(BaseStrategy).parameters
        return [p.name for p in params.values()]
