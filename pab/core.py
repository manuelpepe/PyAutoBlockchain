import time
import logging

from pathlib import Path
from typing import List, Optional
from pab.accounts import load_accounts

from pab.blockchain import Blockchain
from pab.config import load_configs
from pab.strategy import load_strategies
from pab.alert import alert_exception
from pab.queue import Job, QueueLoader


class PAB:
    """ Loads configs, strategies, accounts and tasks. 
    Handles main loop. """
    ITERATION_SLEEP = 60

    def __init__(self, root: Path, keyfiles: Optional[list[Path]] = None, envs: Optional[List[str]] = None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.root = root
        self.config = load_configs(root, envs)
        self.strategies = load_strategies(root)
        self.accounts = load_accounts(keyfiles or [])
        self.blockchain = Blockchain(self.root, self.config, self.accounts)
        self.queue = QueueLoader(self.blockchain, self.strategies).load()

    def start(self):
        while True:
            self.process_queue()
            self.logger.debug(f"Queue iteration finished.")
            self._sleep()

    def process_queue(self):
        for item in self.queue:
            self.process_item(item)

    def process_item(self, item: Job):
        try:
            item.process()
        except Exception as err:
            self.logger.exception(err)
            alert_exception(err, self.config)
            raise err

    def _sleep(self):
        self.logger.debug(f"Sleeping for {self.ITERATION_SLEEP} seconds.")
        time.sleep(self.ITERATION_SLEEP)
