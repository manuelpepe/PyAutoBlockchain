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


Accounts
--------

Accounts, also called *wallets*, are used in blockchains as user controlled addresses that can sign transactions
and data. For info on how to configure a accounts in PAB read :ref:`Loading Accounts`.

To use configured accounts in a BaseStrategy subclass, you can access the :attr:`pab.strategy.BaseStrategy.accounts` attribute
(e.g. `self.accounts[0]`, `self.accounts[1]`).


Contracts
---------

PAB automatically loads the contracts defined in :ref:`Registering Contracts`.
Strategies can fetch them by name using the :attr:`pab.strategy.BaseStrategy.contracts` attribute.

For example:

.. code-block:: python

    self.contracts.get("MY_CONTRACT")


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


Blockchain and Web3
-------------------

To access the underlying Web3_ connection you can use the
:attr:`pab.blockchain.Blockchain.w3` attribute. You can get the current `Blockchain` object from your strategie'
s :attr:`pab.strategy.BaseStrategy.blockchain`.




.. _Web3: https://web3py.readthedocs.io/en/stable/index.html
