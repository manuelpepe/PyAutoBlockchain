# PyAutoBlockchain (PAB)

[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-310/)
[![Integration Tests](https://github.com/manuelpepe/PyAutoBlockchain/actions/workflows/integration-tests-main.yml/badge.svg)](https://github.com/manuelpepe/PyAutoBlockchain/actions/workflows/integration-tests-main.yml)
[![Unit Tests](https://github.com/manuelpepe/PyAutoBlockchain/actions/workflows/unit-tests-main.yml/badge.svg)](https://github.com/manuelpepe/PyAutoBlockchain/actions/workflows/unit-tests-main.yml)
[![Documentation Status](https://readthedocs.org/projects/pyautoblockchain/badge/?version=latest)](https://pyautoblockchain.readthedocs.io/en/latest/?badge=latest)
[![codecov](https://codecov.io/gh/manuelpepe/PyAutoBlockchain/branch/main/graph/badge.svg?token=6Hjb772RWB)](https://codecov.io/gh/manuelpepe/PyAutoBlockchain)


PAB is a framework that helps with development and automation of blockchains related tasks.

With PAB, you can quickstart your blockchain development and prototyping. After running `pab init` to create a new project, you can jump right into developing your own python strategies.

With little configuration, you can connect to any Web3 compatible network using an RPC, load contracts from the network, and use any account you have the Private Key of to authenticate against the network (if you need to make transactions).

PAB also comes with a [pytest plugin](https://pyautoblockchain.readthedocs.io/en/latest/guide/testing.html) to make strategy testing easier, read the docs for more information on how to use it!

Check out our [documentation here!](https://pyautoblockchain.readthedocs.io/en/latest/index.html)

## Installation

Using pip:

```bash
$ pip install PyAutoBlockchain
```

## Usage

Create project in current directory:

```bash
(venv) $ pab init
```

Run project:

```bash
(venv) $ pab run
```

For a substantially more complete guide, head over to our [Official Documentation's Guide](https://pyautoblockchain.readthedocs.io/en/latest/guide/index.html).


## Sample Strategy


PAB will load custom strategies at startup from a `strategies` module in the current working directory.
This module can be a single `strategies.py` file or a `strategies` directory with an `__init__.py` file.

All subclasses of `pab.strategy.BaseStrategy` are loaded as available strategies for tasks, and all must implement
the `run()` method.

Here's a basic sample strategy to give you an idea of the Strategy API:

```python
import csv
from datetime import datetime
from pab.strategy import BaseStrategy

class CompoundAndLog(BaseStrategy):
    """ Finds pool in `controller` for `token`, compounds the given pool for
    `self.accounts[account_index]` and logs relevant data into some csv file. """

    def __init__(self, *args, token: str, controller: str, filepath: str = "compound.csv", account_index: int = 0):
        super().__init__(*args)
        self.filepath = filepath
        self.account = self.accounts[account_index]
        self.token = self.contracts.get(token)
        self.controller = self.contracts.get(controller)
        self.pool_id = self.controller.functions.getPoolId(self.token.address).call()
        if not self.pool_id:
            raise Exception(f"Pool not found for {self.token} in {self.controller}")

    def run(self):
        """ Strategy entrypoint. """
        balance = self.get_balance()
        new_balance = self.compound()
        self.write_to_file(balance, new_balance)
        self.logger.info(f"Current balance is {balance}")

    def compound(self) -> int:
        self.transact(self.account, self.controller.functions.compound, (self.pool_id, ))
        return self.get_balance()

    def get_balance(self) -> int:
        return self.controller.functions.balanceOf(
            self.account.address,
            self.pool_id
        ).call()

    def write_to_file(self, old_balance: int, new_balance: int):
        now = datetime.now().strftime('%Y-%m-%d %I:%M:%S')
        diff = new_balance - old_balance
        with open(self.filepath, 'a') as fp:
            writer = csv.writer(fp)
            writer.writerow([now, new_balance, diff])
```

For more details, read our [Official Documentation's Strategies In-Depth Guide](https://pyautoblockchain.readthedocs.io/en/latest/guide/strategy_development_basics.html#strategies-in-depth).


## Sample Test

This sample test uses two mock contracts to test the sample strategy against a local network:

```python
from strategies import CompoundAndLog

def test_compound_and_log(setup_project, get_strat):
    with setup_project() as pab:
        outfile = Path("/tmp/test.txt")
        params = {
            "filepath": str(outfile),
            "token": "TokenMock",
            "controller": "ControllerMock",
            "account_index": 1,
        }
        strat: CompoundAndLog = get_strat(pab, "CompoundAndLog", params)
        account, controller = strat.account, strat.controller
        # we start with balance 0
        assert (
            controller.functions.balanceOf(account.address, strat.pool_id).call() == 0
        )
        # stake 10 and check balance
        strat.transact(account, controller.functions.stake, (strat.pool_id, 10))
        assert (
            controller.functions.balanceOf(account.address, strat.pool_id).call() == 10
        )
        # and after the strategy compounds balance should be 20
        strat.run()
        assert (
            controller.functions.balanceOf(account.address, strat.pool_id).call() == 20
        )
        # also check log was generated correctly
        assert outfile.read_text().strip() == "10,20,10"
```

For more details, read our [Official Documentation's Testing Guide](https://pyautoblockchain.readthedocs.io/en/latest/guide/strategy_development_basics.html#strategies-in-depth).


## Development

### Testing

#### Unit Tests

To run unit tests:

```bash
(venv) $ pip install -e .
(venv) $ pip install requirements-dev.txt
(venv) $ ./tests.sh
```

#### Integration tests

The recommended way to run integration-tests is with [act](https://github.com/nektos/act).

With act you can run:

```
$ act -j integration-tests
```

to run integration from the github actions tests inside a docker container.


The other way is to use local installations of [truffle](https://github.com/trufflesuite/truffle) and [ganache](https://github.com/trufflesuite/ganache) and run:

```
$ ./integration-tests.sh
```

For more information on integration tests see [Integration Tests README](integration-tests/README.md).
