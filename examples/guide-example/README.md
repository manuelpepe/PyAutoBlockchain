# Example PAB Project

This project could be executed, if you were to set a valid endpoint in the `.env` file and replace the placeholder contracts with
real ones.

Nonetheless, this is mostly to give you an idea of how to structure a PAB projects.

You can see some configuration info is set in the `.env` file (which is gitignored) and some
(arguably) not so sensitive configs are set in the `config.json` file (which is not gitignored).

A simple `CompoundAndLog` strategy is defined in `strategies/compound.py` and imported in `strategies/__init__.py` for
PAB to discover it. An example this short could also be in a single `strategies.py` file, but
a directory structure should be cleaner for more complex strategies.

Two contracts are used by the strategy, so both of them are defined in `contracts.json`, and have
their corresponding ABIs inside the `abis/` directory.

A single task is defined in `tasks.json` to run the `CompoundAndLog` strategy, passing the names of the
needed contracts as parameters. This task is set to repeat every 24hs.