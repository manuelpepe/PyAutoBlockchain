# Example PAB Project

This example project aims to give you an idea of how to structure PAB projects.

You can see that sensitive configuration info is set in the `.env` file (which is gitignored) and some
(arguably) not so sensitive configs are set in the `config.json` file (which is not gitignored). Another option is to set non-sensitive data in `.env` and use `.env.prod` for sensitive data, specifying `-e prod` when running live.

A simple `CompoundAndLog` strategy is defined in `strategies/compound.py` and imported in `strategies/__init__.py` for
PAB to discover it. An example this short could also be in a single `strategies.py` file, but
this directory structure should be cleaner for more complex strategies.

Two contracts are used by the strategy, so both of them are defined in `contracts.json`, and have
their corresponding ABIs inside the `abis/` directory.

Two tasks are defined in `tasks.json` to compound some single-asset pools in a controller contract for two
different accounts. Both use the `CompoundAndLog` strategy, passing the names of the needed contracts and the account index as parameters to the strategy.

The two accounts used are loaded from private keys set in `.env` as `PAB_PK0` and `PAB_PK1`. They are commented so tests don't break when (as they are not proper private keys).


# Testing the project

You can use `pytest` to test this project, remember to `pip install -r requirements.txt` beforehand.

Also read the [PAB Testing Guide](https://pyautoblockchain.readthedocs.io/en/latest/guide/testing.html).
