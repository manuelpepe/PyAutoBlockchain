.. _Strategy Development:

Strategy Development
====================


Custom Strategies are automatically loaded when runing `pab run`.
PAB loads your strategies from a `strategies` module at your current working directory.

Any subclass of :class:`pab.strategy.BaseStrategy` in the strategies module can be used
to run a task. For more info on how to configure tasks, see :ref:`Configuring Tasks`.


Basic Strategy
##############

Open `strategies/__init__.py` and write the following:

.. code-block:: python
   :linenos:

    from pab.strategy import BaseStrategy
    from pab.utils import amountToDecimal

    class LogBalanceToFileStrategy(BaseStrategy):
        def __init__(self, *args, accix: int = 0):
            super().__init__(*args)
            self.user = self.accounts[0]

        def run(self):
            balance = self.blockchain.w3.get_balance(self.user)
            self.logger.info(f"Balance: {amountToDecimal(balance)})


This simple strategy will only log the balance of some account.
It uses the `BaseStrategy.accounts` to retrieve the account at the `accix` index, and the current blockchain
connection from `BaseStrategy.blockchain.w3` to get the account balance.



.. _Strategies InDepth:

Strategies In-Depth
###################

.. _Strategies InDept Accounts:

Accounts
--------

Accounts, also called *wallets*, are used in blockchains as user controlled addresses that can sign transactions
and data. For info on how to configure a accounts in PAB read :ref:`Loading Accounts`.

To use configured accounts in a BaseStrategy subclass, you can access the :attr:`pab.strategy.BaseStrategy.accounts` attribute
(e.g. `self.accounts[0]`, `self.accounts[1]`).


.. code-block:: python

    class MyStrategy(BaseStrategy):
        def run(self):
            user = self.accounts[0]


Accounts Attributes
+++++++++++++++++++

Accounts in `self.accounts` are instances of LocalAccount_.


Loading Order
+++++++++++++

As you see in :ref:`Loading Accounts`, there are two ways of loading accounts but only one list.
The way the list is filled is by first loading accounts from environment variables into their fixed indexes,
and then filling the gaps from 0 to N with keyfiles.

This means that if you have the following environment variables:


.. code-block:: bash

    # .env.prod
    PAB_PK1=ACC-A
    PAB_PK2=0xACC-B
    PAB_PK5=0xACC-C


And you run with two keyfiles like this:

.. code-block:: bash

    $ pab run -e prod -k ACC-D.keyfile,ACC-E.keyfile


The accounts dictionary for a strategy will look like this:

.. code-block:: bash

    >>> print(self.accounts)
    {
        0: LocalAccount("0xACC-D"),
        1: LocalAccount("0xACC-A"),
        2: LocalAccount("0xACC-B"),
        3: LocalAccount("0xACC-E"),
        5: LocalAccount("0xACC-C")
    }

To avoid the confusion that using both methods might cause, we recomend you stick to one method of loading accounts.


Contracts
---------

PAB automatically loads the contracts defined in :ref:`Registering Contracts`.
Strategies can fetch them by name using the :attr:`pab.strategy.BaseStrategy.contracts` attribute.

For example:

.. code-block:: python

    class MyStrategy(BaseStrategy):
        def run(self):
            contract = self.contacts.get("MY_CONTRACT")


.. _Strategies InDept Transactions:

Transactions
------------

Subclasses of BaseStrategy will have a :meth:`pab.strategy.BaseStrategy.transact` method that you can use to sign and send
transactions.

For example:

.. code-block:: python

    class MyStrategy(BaseStrategy):
        def run(self):
            user = self.accounts[0]
            contract = self.contacts.get("MY_CONTRACT")
            params = ("param1", 2)
            rcpt = self.transact(user, contract.functions.someFunction, params)



Read-Only Queries
-----------------

You can make readonly queries directly from the contract, without using `self.transact`.

.. code-block:: python

    class MyStrategy(BaseStrategy):
        def run(self):
            contract = self.contacts.get("MY_CONTRACT")
            params = ("param1", 2)
            some_data = contract.functions.getSomeData(*params).call()


Read-Only queries do not consume gas.


Blockchain and Web3
-------------------

To access the underlying Web3_ connection you can use the
:attr:`pab.blockchain.Blockchain.w3` attribute. You can get the current `Blockchain` object from your strategie'
s :attr:`pab.strategy.BaseStrategy.blockchain`.



.. _Web3: https://web3py.readthedocs.io/en/stable/index.html
.. _LocalAccount: https://eth-account.readthedocs.io/en/latest/eth_account.signers.html#eth_account.signers.local.LocalAccount
