import random
import string

from pab.strategy import BaseStrategy

class SampleStrategy(BaseStrategy):
    def __init__(self, *args, contract_name: str = ''):
        super().__init__(*args)
        self.contract = self.contracts.get(contract_name)

    def run(self):
        self.check_string()
        self.check_integer()
        self.check_bool()

    def check_string(self):
        newval = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        old = self.contract.functions.getString().call()
        assert old != newval
        self.transact(self.accounts[0], self.contract.functions.setString, (newval, ))
        new_from_contract = self.contract.functions.getString().call()
        assert newval == new_from_contract

    def check_integer(self):
        old = self.contract.functions.getInt().call()
        newval = old + 1
        assert old != newval
        self.transact(self.accounts[0], self.contract.functions.setInt, (newval, ))
        new_from_contract = self.contract.functions.getInt().call()
        assert newval == new_from_contract

    def check_bool(self):
        old = self.contract.functions.getBool().call()
        newval = not old
        assert old != newval
        self.transact(self.accounts[0], self.contract.functions.setBool, (newval, ))
        new_from_contract = self.contract.functions.getBool().call()
        assert newval == new_from_contract
