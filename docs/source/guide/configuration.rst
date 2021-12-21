Configuration
=============


Blockchain Connection Setup
---------------------------

An RPC is needed for PAB to communicate with the blockchain networks.
Some known RPCs with free tiers are Infura_ and MaticVigil_.

RPC endpoint can be loaded from the `PAB_CONF_ENDPOINT` environment variable or from the `endpoint` config.


.. _Loading Accounts:

Loading Accounts
----------------

Multiple accounts can be loaded dynamically loaded from the environment or keyfiles to use in the strategies.

You can set the environment variables `PAB_PK1`, `PAB_PK2`, etc as the private keys for the accounts.

Another option is to use keyfiles, which can be created with `pab create-keyfile`. You can specify keyfiles to load with `pab run --keyfiles key1.file,key2.file`. Accounts loaded through keyfiles require a one-time interactive authentication at the start of the execution.

All accounts are then loaded for all strategies into `self.accounts[0]`, `self.accounts[1]`, etc...


For example:

.. code-block:: bash

    $ export PAB_PK0="0xSomePrivateKey"
    $ pab run


.. _Registering Contracts:

Registering Contracts
---------------------

Contracts are loaded from the `contracts.json` file at the project root. An example would be:

.. code-block:: json

    {
        "MYTOKEN": {
            "address": "0x12345",
            "abifile": "mytoken.abi"
        }
    }

In this example, you also need to create the abifile at `abis/mytoken.abi` with the ABI data. You need to do this for all contracts.

Strategies can then get and use this contract with `self.contracts.get("MYTOKEN")`.


.. _Configuring Tasks:

Configuring Tasks
-----------------

Tasks are loaded from the `tasks.json` file at the project root.
The  following example defines a single task to execute, using the strategy `BasicCompound` that repeats every 24hs.

Multiple contract names (BNB, WBTC, PAIR, MASTERCHEF, ROUTER) are passed to the strategy as params. The strategy later uses these names to query the contracts from `BaseStrategy.contracts`.

.. code-block:: json

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

Tasks are defined as dictionaries with:

* `strategy`: Class name of strategy (must be subclass of `pab.strategy.BaseStrategy`, see `pab list-strategies`)
* `name`: Name, just for logging.
* `params`: Dictionary with strategy parameters. (see `pab list-strategies -v`)
* `repeat_every`: _Optional_. Dictionary with periodicity of the process, same arguments as `datetime.timedelta`.

Run `pab list-strategies -v` to see available strategies and parameters.


.. _Infura: https://infura.io/
.. _MaticVigil: https://rpc.maticvigil.com/