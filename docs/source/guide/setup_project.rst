Setup Project
#############


Create project directory and venv
=================================

First you need to create a directory to contain your project files
and create a virtualenv.

.. code-block:: bash

    $ mkdir -p ~/projects/MyNewProject
    $ python3.10 -m venv venv
    $ source venv/bin/activate


Install PAB and initialize project
==================================

Then install the `PyAutoBlockchain` dependency in your virtualenv
and run `pab init` to create the basic project structure.

.. code-block:: bash

    (venv) $ pip install PyAutoBlockchain
    (venv) $ pab init  # Initialize project in current directory


.. _Project Structure:

Project Structure
=================


Barebones
---------

This is an example of the most basic structure required by a PAB project.

.. code-block::

    MyPABProject
    ├── abis
    │   └── SomeSmartContract.abi
    ├── .env
    ├── config.json
    ├── contracts.json
    ├── tasks.json
    └── strategies.py

This structure does not have tests.

Recommended
-----------

A better project structure that takes into account testing with pytest.

This is the recommended structure when testing a PAB project:

.. code-block::

    MyPABProject
    ├── abis
    │   └── SomeSmartContract.abi
    ├── .env
    ├── config.json
    ├── contracts.json
    ├── tasks.json
    ├── strategies.py
    ├── requirements.txt   # If you have extra dependencies
    ├── pytest.ini
    └── tests
        ├── __init__.py
        ├── conftest.py
        ├── truffle        # Default directory for testing contracts source.
        │   ├── contracts
        │   │   ├── MainContract.sol
        │   │   └── AnotherContract.sol
        │   ├── migrations
        │   │   └── 1_initial_migration.js
        │   └── truffle-config.js
        └── test_basic.py


For more info on testing strategies see :ref:`Testing`.
