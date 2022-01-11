.. _Testing:

Testing
#######

PAB comes with a pytest_ plugin ``pab.test``. It allows you to test
your strategies against local deployments of Smart Contracts by providing some
usefull functionallity like starting a Ganache_ server, building and deploying
your contracts with Truffle_ and automatically fill in some necessary/usefull
info like Ganache test accounts private keys and connection endpoint, and the
temporary contract addresses on the local network.


Example Use Case
================

Say you have a strategy that increments a counter on a Smart Contract every time it runs
by calling a ``incrementCounter()`` method on the contract.

Maybe a good test would be to deploy a contract into a test network, run the strategy a
couple of times and check that the counter is correctly updated. The PAB.test plugin eases
this process, and allows you to easily write an automated test that you can run through ``pytest``.

You would only need a truffle project with one contract that has a compatible ABI, this can be a Mock or even
the live contract code if you have access to it.

For our example:

.. code-block:: solidity
    :linenos:

    contract Counter {
        unit8 counter;

        constructor() {
            counter = 0;
        }

        function getCounter() public view returns (uint8) {
            return counter;
        }

        function incrementCounter () public {
            counter += 1;
        }
    }

Then, you can write a test like this:

.. code-block:: python
    :linenos:

    from strategies import MyStrategy

    def test_asd(setup_project, get_strat):
        with setup_project() as pab:
            params = {"contract": "Counter"}
            strat: MyStrategy = get_strat(pab, 'MyStrategy', params)
            assert strat.vault_token.functions.getCounter().call() == 0
            strat.run()
            assert strat.vault_token.functions.getCounter().call() == 1
            strat.run()
            assert strat.vault_token.functions.getCounter().call() == 2


That's it, when the plugin loads it will deploy the ``Counter`` contract into a test server
and automatically register the contract with the correct test address and ABI.
``Counter`` **doesn't** need to be registered as a contract name.


.. _PAB Testing Plugin:

PAB Testing Plugin
==================

The ``pab.test`` plugin will start a local Ganache_ server, test and deploy
your contracts with Truffle_ and install some usefull fixtures for your tests.

It works in the following way:

When a pytest session is created, the plugin starts a local Ganache server by spawning a
``ganache-cli`` subprocess. It will parse the ganache startup output and collect the connection data
(host, port) and the auto-generated private keys.

After the Ganache server is running, it will run ``truffle deploy`` on all directories
specified in the ``pab-contracts-sources`` config (see :ref:`Plugin Configuration`). The output
of the deployments is parsed to collect the relevant contract data. The default network for deployment
is ```development`` but it can be changed with the ``pab-truffle-network`` config. All contract sources
must be valid `Truffle Project`_.

The last thing done in initialization is to register two pytest fixtures, :func:`pab.test.setup_project`
and :func:`pab.test.get_strat`. You can read more about them in the :ref:`Test API`.

When the pytest session finishes, the ganache process is stopped.

To use the plugin, you must manually install Ganache_ and Truffle_, probably through npm_.
The plugin will check if both dependencies are installed as ``ganache-cli`` and ``truffle``.


Test Case Example
-----------------

The following is a sample test case written with the help of the :ref:`PAB Testing Plugin`.


.. code-block:: python
    :linenos:

    # MyProject/tests/test_basic.py
    def test_basic_run(setup_project, get_strat):
        with setup_project("MyProject") as pab:
            params = {
                "contract_a": "ABC",
                "contract_b": "DEF"
            }
            strat = get_strat(pab, "MyStrategyABC", params)
            strat.run()
            assert strat.contract_a.functions.getSomeValue.call() == 'Some Value'


The example uses the ``setup_project`` fixture to initialize the PAB test project and return
a :class:`pab.core.PAB` instance. Inside the context of ``setup_project``, the ``get_strat`` fixture is used
to retrieve a single strategy from the PAB app, initialized with certain parameters. Finally executes the strategy
and asserts that a side-effect (in this case, a value change on some contract attribute) happened.


.. _Plugin Configuration:

Plugin Configuration
--------------------

To enable the plugin you need to add ``pab.test`` to ``pytest_plugins`` in your ``conftest.py``:

.. code-block:: python
    :linenos:

    # MyProject/tests/conftest.py
    import pytest
    pytest_plugins = ["pab.test"]


You can also change some configurations in your ``pytest.ini``:


.. code-block:: ini

    # MyProject/pytest.ini
    [pytest]
    pab-ignore-patterns-on-copy =
        venv/
    pab-contracts-sources =
        tests/contracts
    pab-truffle-network = development


Ganache Configuration
---------------------

There's not much configuration that's necessary for ganache.
PAB starts the process by running ``ganache-cli`` without extra parameters.
By default, this starts a server in at ``127.0.0.1:8545``.


Truffle Configuration
---------------------

The only necessary configuration for truffle is to correctly setup your network parameters.
Ganache defaults are ``127.0.0.1:8545``, so make sure that there is a network with those parameters.

For example, in your ``truffle-config.js``:


.. code-block:: json

    {
        # More configs above
        networks: {
            development: {
                host: "127.0.0.1",
                port: 8545,
                network_id: "*",
            }
        }
        # More configs below
    }


Recommended Structure
---------------------

A sample project structure can be found at :ref:`Project Structure`.



.. _pytest: https://docs.pytest.org/
.. _Truffle: https://github.com/trufflesuite/truffle)
.. _Ganache: https://github.com/trufflesuite/ganache
.. _npm: https://www.npmjs.com/
.. _Truffle Project: https://trufflesuite.com/docs/truffle/reference/truffle-commands.html#init
