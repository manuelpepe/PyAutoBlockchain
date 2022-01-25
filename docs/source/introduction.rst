.. _Introduction:

Introduction
============

With PAB, you quickstart your blockchain development and prototyping.
After running `pab init` to create a new project, you can jump right into your
strategy development.

With little more configuration, you can connect to any Web3 compatible network using
an RPC, load contracts from the network, and use any account you have the Private Key of to
authenticate against the network (if you need to make transactions).

PAB also comes with a pytest plugin that allows for easy strategy testing (see :ref:`Testing`).


.. _Sample Strategy:

Sample Strategy
---------------

Here's a basic sample strategy to give you an idea of the :ref:`Strategy API`:

.. code-block:: python
   :linenos:

    import csv
    from datetime import datetime
    from pab.strategy import BaseStrategy

    class CompoundAndLog(BaseStrategy):
        """ Finds pool in `controller` for `token`, compounds the given pool for
        `self.accounts[account_index]` and logs relevant data into a csv file. """

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
            """ Calls compound function of the `controller` contract to compound pending profits
            on the `token` pool. """
            self.transact(self.account, self.controller.functions.compound, (self.pool_id, ))
            return self.get_balance()

        def get_balance(self) -> int:
            """ Returns accounts balance on `controller` for `token` pool. """
            return self.controller.functions.balanceOf(
                self.account.address,
                self.pool_id
            ).call()

        def write_to_file(self, old_balance: int, new_balance: int):
            """ Write some number to a file. """
            now = datetime.now().strftime('%Y-%m-%d %I:%M:%S')
            diff = new_balance - old_balance
            with open(self.filepath, 'a') as fp:
                writer = csv.writer(fp)
                writer.writerow([now, new_balance, diff])


BaseStrategy childs can use `self.accounts`, `self.contracts` and `self.transact`. They also need
to implement the `run()` method.

For more information on the Strategy API see :ref:`Strategy API` and :ref:`Strategy Development` docs.
