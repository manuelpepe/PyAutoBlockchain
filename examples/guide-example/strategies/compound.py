import csv

from pab.strategy import BaseStrategy


class CompoundAndLog(BaseStrategy):
    """Finds pool in `masterchef` for `token`, compounds the given pool for
    `self.accounts[account_index]` and logs relevant data into some csv file."""

    def __init__(
        self,
        *args,
        filepath: str = "compound.csv",
        token: str = "",
        masterchef: str = "",
        account_index: int = 0,
    ):
        super().__init__(*args)
        self.filepath = filepath
        self.account = self.accounts[account_index]
        self.token = self.contracts.get(token)
        self.masterchef = self.contracts.get(masterchef)
        self.pool_id = self.masterchef.functions.getPoolId(self.token.address).call()
        if not self.pool_id:
            return RuntimeError(f"Pool not found for {self.token} in {self.masterchef}")

    def run(self):
        balance = self.get_balance()
        new_balance = self.compound()
        self.write_to_file(balance, new_balance)
        self.logger.info(f"Current balance is {balance}")

    def compound(self) -> int:
        self.transact(self.account, self.masterchef.functions.compound, (self.pool_id,))
        return self.get_balance()

    def get_balance(self) -> int:
        return self.masterchef.functions.balanceOf(
            self.account.address, self.pool_id
        ).call()

    def write_to_file(self, old_balance: int, new_balance: int):
        diff = new_balance - old_balance
        with open(self.filepath, "a") as fp:
            writer = csv.writer(fp)
            writer.writerow([old_balance, new_balance, diff])
