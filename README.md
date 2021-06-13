# PyAutoBlockchain (PAB)


[![Tests](https://github.com/manuelpepe/PyAutoBlockchain/actions/workflows/python-app.yml/badge.svg)](https://github.com/manuelpepe/PyAutoBlockchain/actions/workflows/python-app.yml)
[![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/downloads/release/python-390/)

PAB is a framework for developing and running custom tasks in crypto blockchains.


## Installation

Clone the repo and install dependencies.

```bash
$ python3 -m venv venv
$ pip install pab
```


## Usage

```bash
(venv) $ pab create-keyfile [-o keyfile]  # Create keyfile
(venv) $ pab edit-config  # Edit config file
(venv) $ pab list-strategies -v  # List available strategies and parameters
(venv) $ pab run  # Run tasks
```

## Configuration

### Configure wallet and RPC 

Create project config and keyfile:

```bash
(venv) $ pab edit-config
(venv) $ pab create-keyfile
```

You can get register at [MaticVigil](https://rpc.maticvigil.com/) for a free RPC account.

### Adding extra contracts

To use contracts in the strategies you first need to add the abi file to `abis` and 
modify the `contracts.json` file to load it.

For example, given the contract for `MYTOKEN` at `0x12345` create the abifile at `abis/mytoken.abi` and add
to `contracts.json` the following:

```json
{
    "MYTOKEN": {
        "address": "0x12345",
        "abifile": "mytoken.abi"
    }
}
```

### Adding extra strategies

You can add strategies to execute at `strategies.json`.
For example, the following example defines 1 estrategy to execute, using the strategy `CompoundStrategy` 
and the contracts `BNB`, `WBTC`, `PAIR`, `MASTERCHEF` and `ROUTER`.

```json
[
    {
        "strategy": "CompoundStrategy",
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

Strategies are dictionaries with:

* `strategy`: Class name of strategy (must be subclass of `pab.strategy.CompoundStrategy`, see `pab list-strategies`)
* `name`: Name, just for logging.
* `params`: Dictionary with strategy parameters. (see `pab list-strategies -v`)
* `repeat_every`: _Optional_. Dictionary with periodicity of the process, same arguments as `datetime.timedelta`.

Run `pab list-strategies -v` to see available strategies and parameters.

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


## Developing

For details see [ARCHITECTURE.md](ARCHITECTURE.md)


### Running tests

Using pytest:

```bash
(venv) $ pip install -e requirements-dev.txt
(venv) $ ./tests.sh
```