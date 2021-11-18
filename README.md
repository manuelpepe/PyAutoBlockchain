# PyAutoBlockchain (PAB)


[![Tests](https://github.com/manuelpepe/PyAutoBlockchain/actions/workflows/python-app.yml/badge.svg)](https://github.com/manuelpepe/PyAutoBlockchain/actions/workflows/python-app.yml)
[![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/downloads/release/python-390/)

PAB is a framework that helps with development and automation of periodic tasks on blockchains.

For a more in-depth guide see [GUIDE.md](GUIDE.md), the example at [examples](examples/guide-example) or a more complex implementation at [PolyCompounder](https://github.com/manuelpepe/PolyCompounder).

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

Create project: 

```bash
(venv) $ pab init 
```

Run project:

```bash
(venv) $ pab run  # Run tasks
```

## Configuration

### config.json vs Environment Variables

All configurations can be loaded from environment variables (optionally from a `.env` file) or the `config.json` file.
Environment variables follow the name schema `PAB_CONF_<PATH>`.

For example:

* `transactions.timeout` is `PAB_CONF_TRANSACTIONS_TIMEOUT`

### RPC

An RPC is needed for PAB to communicate with the blockchain networks.
Some known RPCs with free tiers are [Infura](https://infura.io/) and [MaticVigil](https://rpc.maticvigil.com/).

RPC endpoint can be loaded from the `PAB_CONF_ENDPOINT` environment variable or from the `endpoint` config.

### Wallet / Private Key

Your private key is loaded from a `key.file` file in the projects root. This file will hold your private key, encrypted with a password of your choosing.

If you need to create a keyfile,To create a keyfile (You will be prompted for a private key and a password):

```bash
(venv) $ pab create-keyfile
```


### Contracts

To use contracts in the strategies you first need to add the abi file to `abis` and modify the `contracts.json` file to load it.

For example, given the contract for `MYTOKEN` at `0x12345` create the abifile at `abis/mytoken.abi` and add to `contracts.json` the following:

```json
{
    "MYTOKEN": {
        "address": "0x12345",
        "abifile": "mytoken.abi"
    }
}
```

### Tasks

You can add tasks to execute at `tasks.json`.
For example, the following example defines 1 task to execute, using the strategy `BaseStrategy` 
and the contracts `BNB`, `WBTC`, `PAIR`, `MASTERCHEF` and `ROUTER`.

```json
[
    {
        "strategy": "BaseStrategy",
        "name": "BNB-WBTC",
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
Custom strategies must be childs of `pab.strategy.BaseStrategy`.

For more info on creating strategies see [GUIDE.md](GUIDE.md) and [PolyCompounder](https://github.com/manuelpepe/PolyCompounder) 
for a different example.


### Email alerts

You can setup email alerts for when something goes wrong.
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

Transaction options are available in `config.json`:

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
