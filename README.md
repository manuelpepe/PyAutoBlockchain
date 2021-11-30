# PyAutoBlockchain (PAB)


[![Tests](https://github.com/manuelpepe/PyAutoBlockchain/actions/workflows/python-app.yml/badge.svg)](https://github.com/manuelpepe/PyAutoBlockchain/actions/workflows/python-app.yml)
[![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/downloads/release/python-390/)

PAB is a framework that helps with development and automation of periodic tasks on blockchains.

PAB allows you to quickly implement strategies without worring about some Web3 implementation details, like connecting to a blockchain, retrieving contracts and sending transactions.

For a sample guide see [GUIDE.md](GUIDE.md), the example at [examples](examples/guide-example) or a more complex implementation at [PolyCompounder](https://github.com/manuelpepe/PolyCompounder).

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

## Basic Concepts


### config.json vs Environment Variables

All configurations can be loaded from environment variables (optionally from a `.env` file) or the `config.json` file.
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


### Accounts

Multiple accounts can be loaded dynamically loaded from the environment or keyfiles to use in the strategies.

You can set the environment variables `PAB_PK1`, `PAB_PK2`, etc as the private keys for the accounts.

Another option is to use keyfiles, which can be created with `pab create-keyfile`. You can specify keyfiles to load with `pab run --keyfiles key1.file,key2.file`. Accounts loaded through keyfiles require a one-time interactive authentication at the start of the execution.

All accounts are then loaded into `BaseStrategy.accounts`.


### Contracts

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
Strategies can then use the contracts through `BaseStrategy.contracts`.


### Tasks

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


### Custom Strategies

`pab` will load custom strategies at startup from a `strategies` module in the current working directory.
This module can be a single `strategies.py` file or a `strategies` directory with an `__init__.py` file.

All subclasses of `pab.strategy.BaseStrategy` are loaded as available strategies for tasks.

For more info on creating strategies see [GUIDE.md](GUIDE.md) and [PolyCompounder](https://github.com/manuelpepe/PolyCompounder) 
for a different example.


### Email alerts

You can setup email alerts for unhandled and handled exceptions.
Add the following to your `config.json`:

```json
{
    "emails": {
        "enabled": true,
        "host": "smtp.host.com",
        "port": 465,
        "address": "email@host.com",
        "password": "password",
        "recipient": "me@host.com"
    }   
}
```


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


## Developing

For details see [ARCHITECTURE.md](ARCHITECTURE.md)


### Running tests

Using pytest:

```bash
(venv) $ pip install -e requirements-dev.txt
(venv) $ ./tests.sh
```
