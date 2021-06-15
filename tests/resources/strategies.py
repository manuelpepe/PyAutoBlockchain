from typing import List

from pab.strategy import BaseStrategy
from pab.blockchain import Blockchain


class CustomStrategy(BaseStrategy):
    """ Custom strategy for testing """

    def __init__(self, blockchain: Blockchain, name: str, test_var: List[str]):
        super().__init__(blockchain, name)
        self.test_var = test_var

    def run(self):
        self.logger.info(f"Running {self.name} with test_var: {self.test_var}")