from typing import List

from pab.strategy import BaseStrategy
from pab.blockchain import Blockchain


class CustomStrategy(BaseStrategy):
    """ Compound strategy for PZAP Pools """

    def __init__(self, blockchain: Blockchain, name: str, test_var: List[str]):
        super().__init__(blockchain, name)
        self.test_var = test_var

    def compound(self):
        """ Runs complete compound process """
        self.logger.info(f"Compounding {self.name} with test_var: {self.test_var}")