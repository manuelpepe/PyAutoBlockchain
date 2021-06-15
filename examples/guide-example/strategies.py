from pab.strategy import CompoundStrategy


class LogBalanceToFileStrategy(CompoundStrategy):
    def __init__(self, *args, filepath: str = "/tmp/default.log", contract: str = None):
        super().__init__(*args)
        self.filepath = filepath
        self.contract = self.blockchain.read_contract(contract)

    def compound(self):
        balance = self.get_balance()
        self.write_to_file(balance)
        self.logger.info(f"Current balance is {balance}")

    def get_balance(self) -> str:
        return str(self.contract.functions.balanceOf(self.blockchain.owner).call())
    
    def write_to_file(self, data: str):
        with open(self.filepath, 'a') as fp:
            fp.write(data + "\n")