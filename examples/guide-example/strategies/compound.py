import csv

from pab.strategy import BaseStrategy


class CompoundAndLog(BaseStrategy):
    """Finds pool in for `token` in `controller` contract, compounds the given pool for
    `self.accounts[account_index]` and logs relevant data into some csv file."""

    def __init__(
        self,
        *args,
        token: str,
        controller: str,
        filepath: str = "compound.csv",
        account_index: int = 0,
    ):
        super().__init__(*args)
        self.filepath = filepath
        self.account = self.accounts[account_index]
        self.token = self.contracts.get(token)
        self.controller = self.contracts.get(controller)
        self.pool_id = self.controller.functions.getPoolId(self.token.address).call()
        if not self.pool_id:
            return Exception(f"Pool not found for {self.token} in {self.controller}")

    def run(self):
        balance = self.get_balance()
        new_balance = self.compound()
        self.write_to_file(balance, new_balance)
        self.logger.info(f"Current balance is {balance}")

    def compound(self) -> int:
        self.transact(self.account, self.controller.functions.compound, (self.pool_id,))
        return self.get_balance()

    def get_balance(self) -> int:
        return self.controller.functions.balanceOf(
            self.account.address, self.pool_id
        ).call()

    def write_to_file(self, old_balance: int, new_balance: int):
        diff = new_balance - old_balance
        with open(self.filepath, "a") as fp:
            writer = csv.writer(fp)
            writer.writerow([old_balance, new_balance, diff])
