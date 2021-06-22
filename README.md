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

A basic config file without alerts enabled might look like:

```json
{
    "blockchain": "POLYGON",
    "chainId": 137,
    "endpoint": "https://mainnet.infura.io/v3/your_key",
    "myAddress": "0xyour_address"
}

```

You can get a free RPC endpoint for most known blockchains (e.g. [Infura](https://infura.io/) or [MaticVigil](https://rpc.maticvigil.com/)).

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

### Setting up tasks

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


### Creating custom strategies

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
