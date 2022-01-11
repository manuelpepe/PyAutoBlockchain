from __future__ import annotations

import time
import logging

from pathlib import Path
from pab.accounts import load_accounts

from pab.blockchain import Blockchain
from pab.config import load_configs
from pab.strategy import load_strategies
from pab.alert import alert_exception
from pab.task import Task, TaskFileParser, TaskList


class PAB:
    """Loads configs, strategies, accounts and tasks.
    Handles main loop."""

    ITERATION_SLEEP = 60

    def __init__(
        self,
        root: Path,
        keyfiles: list[Path] | None = None,
        envs: list[str] | None = None,
        load_tasks: bool = True,
    ):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.root = root
        self.config = load_configs(root, envs)
        self.strategies = load_strategies(root)
        self.accounts = load_accounts(keyfiles or [])
        self.blockchain = Blockchain(self.root, self.config, self.accounts)
        self.tasks: TaskList | list = []
        if load_tasks:
            self.tasks = TaskFileParser(root, self.blockchain, self.strategies).load()

    def start(self):
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
            alert_exception(err, self.config)
            raise err

    def _sleep(self):
        self.logger.debug(f"Sleeping for {self.ITERATION_SLEEP} seconds.")
        time.sleep(self.ITERATION_SLEEP)
