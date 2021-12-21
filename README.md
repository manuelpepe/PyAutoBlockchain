# PyAutoBlockchain (PAB)

[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-310/)
[![Integration Tests](https://github.com/manuelpepe/PyAutoBlockchain/actions/workflows/integration-tests.yml/badge.svg)](https://github.com/manuelpepe/PyAutoBlockchain/actions/workflows/integration-tests.yml)
[![Unit Tests](https://github.com/manuelpepe/PyAutoBlockchain/actions/workflows/python-app.yml/badge.svg)](https://github.com/manuelpepe/PyAutoBlockchain/actions/workflows/python-app.yml)
[![Documentation Status](https://readthedocs.org/projects/pyautoblockchain/badge/?version=latest)](https://pyautoblockchain.readthedocs.io/en/latest/?badge=latest)
[![codecov](https://codecov.io/gh/manuelpepe/PyAutoBlockchain/branch/master/graph/badge.svg?token=6Hjb772RWB)](https://codecov.io/gh/manuelpepe/PyAutoBlockchain)


PAB is a framework that helps with development and automation of periodic tasks on blockchains.

PAB allows you to quickly implement Strategies without worring about some Web3 implementation details, like connecting to a blockchain, retrieving contracts and sending transactions.

Check out our [documentation here!](https://pyautoblockchain.readthedocs.io/en/latest/index.html)

## Installation

Using pip:

```bash
$ pip install PyAutoBlockchain
```


### With PABUI

Install with [PABUI](https://github.com/manuelpepe/pabui) extension:

```bash
$ pip install PyAutoBlockchain[ui]
```

And run PABUI from your projects directory:
```bash
$ ls
abis/  config.json  contracts.json  strategies.py  tasks.json  venv/
$ pabui
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
    """ Finds pool in `masterchef` for `token`, compounds the given pool for 
    `self.accounts[account_index]` and logs relevant data into some csv file. """

    def __init__(self, *args, filepath: str = "compound.csv", token: str = '', masterchef: str = '', account_index: int = 0):
        super().__init__(*args)
        self.filepath = filepath
        self.account = self.accounts[account_index]
        self.token = self.contracts.get(token)
        self.masterchef = self.contracts.get(masterchef)
        self.pool_id = self.masterchef.functions.getPoolId(self.token.address).call()
        if not self.pool_id:
            raise Exception(f"Pool not found for {self.token} in {self.masterchef}")

    def run(self):
        """ Strategy entrypoint. """
        balance = self.get_balance()
        new_balance = self.compound()
        self.write_to_file(balance, new_balance)
        self.logger.info(f"Current balance is {balance}")

    def compound(self) -> int:
        self.transact(self.account, self.masterchef.functions.compound, (self.pool_id, ))
        return self.get_balance()

    def get_balance(self) -> int:
        return self.masterchef.functions.balanceOf(
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


## Accounts

Multiple accounts can be loaded dynamically loaded from the environment or keyfiles to use in the strategies.

You can set the environment variables `PAB_PK1`, `PAB_PK2`, etc as the private keys for the accounts.

Another option is to use keyfiles, which can be created with `pab create-keyfile`. You can specify keyfiles to load with `pab run --keyfiles key1.file,key2.file`. Accounts loaded through keyfiles require a one-time interactive authentication at the start of the execution.

All accounts are then loaded for all strategies into `self.accounts[0]`, `self.accounts[1]`, etc...


## Contracts

Contracts are loaded from the `contracts.json` file at the project root. An example would be:

```
{
    "MYTOKEN": {
        "address": "0x12345",
        "abifile": "mytoken.abi"
    }
}
```

In this example, you also need to create the abifile at `abis/mytoken.abi` with the ABI data. You need to do this for all contracts.

Strategies can then get and use this contract with `self.contracts.get("MYTOKEN")`.


## Tasks

Tasks are loaded from the `tasks.json` file at the project root.
The  following example defines a single task to execute, using the strategy `BasicCompound` that repeats every 24hs.

Multiple contract names (BNB, WBTC, PAIR, MASTERCHEF, ROUTER) are passed to the strategy as params. The strategy later uses these names to query the contracts from `BaseStrategy.contracts`.

```json
[
    {
        "strategy": "BasicCompound",
        "name": "Compound BNB-WBTC",
        "repeat_every": {
            "days": 1
        },
        "params": {
            "swap_path": ["BNB", "WBTC"],
            "pair": "PAIR",
            "masterchef": "MASTERCHEF",
            "router": "ROUTER",
            "pool_id": 11
        }
    }
]
```

Tasks are defined as dictionaries with:

* `strategy`: Class name of strategy (must be subclass of `pab.strategy.BaseStrategy`, see `pab list-strategies`)
* `name`: Name, just for logging.
* `params`: Dictionary with strategy parameters. (see `pab list-strategies -v`)
* `repeat_every`: _Optional_. Dictionary with periodicity of the process, same arguments as `datetime.timedelta`.

Run `pab list-strategies -v` to see available strategies and parameters.


## Configuration

Configs can be loaded from environment variables (optionally from a `.env` file) or from the `config.json` file.

Environment variables follow the name schema `PAB_CONF_<PATH>`.

For example, `transactions.timeout` can be set in `.env` as:

```
PAB_CONF_TRANSACTIONS_TIMEOUT=100
```

or in `config.json` as:

```
{
    "transactions": {
        "timeout": 100
    }
}
```

Multiple `.env.name` files can be loaded with `pab -e name,name2 run`.


### RPC

An RPC is needed for PAB to communicate with the blockchain networks.
Some known RPCs with free tiers are [Infura](https://infura.io/) and [MaticVigil](https://rpc.maticvigil.com/).

RPC endpoint can be loaded from the `PAB_CONF_ENDPOINT` environment variable or from the `endpoint` config.


### Transaction settings

Default transaction options are available through the following configs:

```
{
    "transactions": {
        "timeout": 200,
        "gasPrice": {
            "number": "1.1",
            "unit": "gwei"
        },
        "gas": {
            "useEstimate": false,
            "exact": 200000
        }
    }
}
```

### Email alerts

You can setup email alerts for unhandled and handled exceptions.
Add the following to your `config.json`:

```json
{
    "emails": {
        "enabled": true,
        "host": "smtp.host.com",
        "port": 465,
        "user": "email@host.com",
        "password": "password",
        "recipient": "me@host.com"
    }   
}
```


## Developing

### Testing

#### Unit Tests

To run unit tests:

```bash
(venv) $ pip install -e requirements-dev.txt
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
