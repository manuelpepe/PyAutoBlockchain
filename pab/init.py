from __future__ import annotations

import os
import json

from contextlib import AbstractContextManager
from pathlib import Path

from projectutils.init import Directory, File, Tree
from pab.config import SCHEMA


class chdir(AbstractContextManager):
    """Non thread-safe context manager to change the current working directory.
    In the future replace with built-in version: https://github.com/python/cpython/pull/28271"""

    def __init__(self, path):
        self.path = path
        self._old_cwd = []

    def __enter__(self):
        self._old_cwd.append(os.getcwd())
        os.chdir(self.path)

    def __exit__(self, *excinfo):
        os.chdir(self._old_cwd.pop())


SAMPLE_ABI_DATA = '[{"This ABI is not valid. Only serves as an example."}]'
SAMPLE_CONFIG_DATA = json.dumps(SCHEMA.defaults(), indent=4)
SAMPLE_TASKS_DATA = """[
    {
        "name": "Example Task",
        "strategy": "SampleStrategy",
        "params": {
            "contract_name": "MyContract",
            "some_param": 3.1416
        },
        "repeat_every": {
            "hours": 1
        }
]"""
SAMPLE_CONTRACTS_DATA = """{
    "MyContract": {
        "address": "0x000",
        "abifile": "MyContract.abi"
    }
}"""
SAMPLE_STRATEGIES_DATA = """from pab.strategy import BaseStrategy

class SampleStrategy(BaseStrategy):
    def __init__(self, *args, contract_name: str, some_param: int):
        super().__init__(*args)
        self.some_param = some_param
        self.contract = self.contracts.get(contract_name)

    def run(self):
        args = (self.some_param, "another_param")
        self.transact(self.accounts[0], self.contract.functions.some_function, args)
"""
GITIGNORE_CONTENT = """## .env* files hold sensitive data.
.env*

## If you're using a keyfile, remember that it's probably not safe
## to commit it to any remote. Keep that in mind if you're using a different name for it.
key.file

## Probably don't want to version the log
pab.log
"""
GITIGNORE_WARNING = "Warning! .gitignore was not created because it already exists. You should probably gitignore .env* files."

README_DATA = """
# PAB Project

This project was created with using `pab init`.

[Read the docs!](https://pyautoblockchain.readthedocs.io/en/latest/).
"""

TESTS_README_DATA = """
# Strategy Testing

For strategy testing you should have installed `ganache-cli` and `truffle`.

[Read the docs!](https://pyautoblockchain.readthedocs.io/en/latest/guide/testing.html).


## First steps

Initialize your truffle project at `tests/truffle`.

```
$ cd tests/truffle
$ truffle init
```
"""

CONFTEST_CONTENT = """
import pab.test  # noqa: F401

pytest_plugins = ["pab.test"]
"""


TREE = [
    Directory("abis", [File("MyContract.abi", SAMPLE_ABI_DATA)]),
    Directory("strategies", [File("__init__.py", SAMPLE_STRATEGIES_DATA)]),
    Directory(
        "tests",
        [
            Directory(
                "truffle",
                [
                    File(
                        "README.md",
                        "Initialize your truffle project here with `truffle init`",
                    )
                ],
            ),
            File("README.md", TESTS_README_DATA),
            File("conftest.py", CONFTEST_CONTENT),
        ],
    ),
    File("README.md", README_DATA),
    File("config.json", SAMPLE_CONFIG_DATA),
    File("tasks.json", SAMPLE_TASKS_DATA),
    File("contracts.json", SAMPLE_CONTRACTS_DATA),
    File("requirements-dev.txt", "pytest\n"),
    File("requirements.txt", "PyAutoBlockchain\n"),
    File(".gitignore", GITIGNORE_CONTENT, optional=True, warning=GITIGNORE_WARNING),
]


def initialize_project(directory: Path):
    tree = Tree(TREE)
    tree.create(directory)
