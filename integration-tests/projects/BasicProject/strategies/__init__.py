from pab.strategy import BaseStrategy

class SampleStrategy(BaseStrategy):
    def __init__(self, *args, contract_name: str = ''):
        super().__init__(*args)
        self.contract = self.blockchain.read_contract(contract_name)

    def run(self):
        # Processing here
        ...
