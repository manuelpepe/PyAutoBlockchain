## Introduction

This document will guide you through the first steps on creating your own strategies.

For a more complex example see [PolyCompounder](https://github.com/manuelpepe/PolyCompounder).

This guide assumes you're using an [unix system](https://www.youtube.com/watch?v=dFUlAQZB9Ng).

The cli to interact with PyAutoBlockchain is `pab`.

You can find the complete implementation of the guide in [examples](examples/guide-example) or a more complex implementation at [PolyCompounder](https://github.com/manuelpepe/PolyCompounder).


## Setup

### 1. Creating a virtualenv for your project

Create a directory and virtualenv for your project:

```
$ mkdir -p ~/projects/BlockchainTasks
$ python3 -m venv venv
$ source venv/bin/activate
```

### 2. Install PyAutoBlockchain

Using pip:

```
(venv) $ pip install PyAutoBlockchain
```

## Strategy Development

Custom strategies are automatically loaded when runing `pab run`.
PAB loads your strategies from a `strategies` module at your current working directory.

Create a `strategies.py` file and write the following:

```python
from pab.strategy import BaseStrategy


class LogBalanceToFileStrategy(BaseStrategy):
    def __args__(self, *args, filepath: str = "/tmp/default.log", contract_name: str = None):
        super().__init__(args)
        self.filepath = filepath
        self.contract = self.blockchain.read_contract(contract_name)

    def run(self):
        balance = self.get_balance()
        self.write_to_file(balance)
        self.logger.info(f"Current balance is {balance}")

    def get_balance(self) -> str:
        return str(self.contract.functions.balanceOf(self.blockchain.owner).call())
    
    def write_to_file(self, data: str):
        with open(self.filepath, 'a') as fp:
            fp.write(data + "\n")
```


Here we're creating a basic strategy that will query the your wallet's balance in a contract 
and write it to a file so you can use it for logging or analysis.

In the constructor we're requesting the `filepath` and `contract_name` arguments, storing the `filepath` for later and
using the `contract_name` with `self.blockchain.read_contract` to store a reference to the Web3 contract.

The `run` method, which **must** be defined, is the start point of the strategy. Here we're using two separate
methods to first get the balance from the contract (using the `balanceOf` contract function), and then writing it to a file.
We're also logging the balance to get some info on the screen without needing to read the output file.


## Configuration

### 1. Basic configuration (config.json)

You can change PyAutoBlockchain basic configs, such as the RPC endpoint and your wallet address, in the `config.json` file.

Use the following command to get a basic structure and edit to suit you're needs.

```
(venv) $ pab edit-config
```

For this guide we'll use a configuration such as:

```json
{
    "blockchain": "ETHEREUM",
    "chainId": 1,
    "endpoint": "https://mainnet.infura.io/v3/YOUR_API",
    "myAddress": "0xYOUR_ADDRESS"
}
```

You can get a free RPC endpoint for most known blockchains (e.g. [Infura](https://infura.io/) or [MaticVigil](https://rpc.maticvigil.com/)).

### 2. Create keyfile

To make transactions in the blockchain you'll need a keyfile.
You can use this utility to create one from your private key and a password:

```
(venv) $ pab create-keyfile
```

### 3. Register contracts

Registering a contract allows your strategies to call its functions.
To do this you'll need it's contract address and ABI.

For this example, add this to your `contracts.json` file:

```json
{
    "MATIC": {
        "address": "0x7D1AfA7B718fb893dB30A3aBc0Cfc608AaCfeBB0",
        "abifile": "matic.abi"
    }
}
```

and create the abi file in the `abis` directory:

```
(venv) $ mkdir abis
(venv) $ curl "http://api.etherscan.io/api?module=contract&action=getabi&address=0x7D1AfA7B718fb893dB30A3aBc0Cfc608AaCfeBB0&format=raw" > abis/matic.abi
```

### 4. Create tasks

A list of tasks to run will be loaded from a `tasks.json` file at your CWD.

Create a `tasks.json` file with the following content:

```json
[
    {
        "strategy": "LogBalanceToFileStrategy",
        "name": "MATIC Balance",
        "repeat_every": {
            "hours": 1
        },
        "params": {
            "filepath": "balance-history.txt",
            "contract": "MATIC"
        }
    }
]
```

This will make PAB run a task using the strategy we defined previously. It will create the strategy using the parameters
in `params`, passing them as keyword arguments the strategy constructor, and repeat the tasks every hour.

Here we're telling it to read the balance from the `MATIC` contract (defined in `contracts.json` and `abis/`) and write it to
the `balance-history.txt` file every hour.

## Run

Now you can just execute `pab run` and you should see output like this:

```
$ pab run
Enter wallet password:
Running strategy MATIC Balance on ETHEREUM#5
Current balance is 0
Done with MATIC Balance on ETHEREUM#5
$ cat balance-history.txt
0
```