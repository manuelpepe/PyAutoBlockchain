import os
from abc import ABC, abstractmethod
from contextlib import AbstractContextManager
from pathlib import Path
from typing import List, Optional

from pab.config import DEFAULTS_CONFIG_FILE


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


class Node(ABC):
    def __init__(self, path: str):
        self.path = Path(path)
        if "/" in str(self.path):
            raise ValueError("Path can't traverse nodes.")
        self.errors = []

    @abstractmethod
    def create(self):
        ...


class Directory(Node):
    def __init__(self, path: Path, childs: List[Node] = []):
        super().__init__(path)
        self.childs = childs

    def create(self):
        self.path.mkdir()
        with chdir(self.path):
            for child in self.childs:
                child.create()


class File(Node):
    def __init__(self, path: Path, content: str, optional: bool = False, warning: Optional[str] = None):
        super().__init__(path)
        self.content = content
        self.optional = optional
        self.warning = warning

    def create(self):
        if self.path.exists():
            if self.warning:
                self.warn()
            if self.optional:
                return
            raise FileExistsError(self.path)
        self.path.write_text(self.content)
    
    def warn(self):
        print(self.warning)
        

class Tree:
    def __init__(self, nodes: List[Node]):
        self.nodes = nodes

    def create(self):
        for node in self.nodes:
            node.create()


SAMPLE_ABI_DATA = '[{"This ABI is not valid. Only serves as an example."}]'
SAMPLE_CONFIG_DATA = DEFAULTS_CONFIG_FILE.read_text()
SAMPLE_TASKS_DATA = """{
    "name": "Example Task",
    "strategy": "SampleStrategy",
    "params": {
        "contract_name": "MyContract",
        "some_param": 3.1416
    },
    "repeat_every": {
        "hours": 1
    }
}"""
SAMPLE_CONTRACTS_DATA = """{
    "MyContract": {
        "address": "0x000",
        "abifile": "MyContract.abi"
    }
}"""
SAMPLE_STRATEGIES_DATA = """from pab.strategy import BaseStrategy

class SampleStrategy(BaseStrategy):
    def __init__(self, *args, contract_name: str = '', some_param: int = -1):
        super().__init__(*args)
        self.some_param = some_param
        self.contract = self.blockchain.read_contract(contract_name)

    def run(self):
        # Processing here
        ...
"""
GITIGNORE_CONTENT = """# config.json holds your address and other authentication details (email, rcp).
config.json

# If you're using a keyfile, remember that it's probably not safe
# to commit it to any remote. Keep that in mind if you're using a different name for it.
key.file
"""
GITIGNORE_WARNING = """Warning! .gitignore was not created because it already exists.
If you're versioning this project, remember that your key.file and the config.json files might not be secure to version and should be .gitignored or similar.
Commit them at your own discretion."""



TREE = [
    Directory("abis", [
        File("MyContract.abi", SAMPLE_ABI_DATA)
    ]),
    Directory("strategies", [
        File("__init__.py", SAMPLE_STRATEGIES_DATA)
    ]),
    File("config.json", SAMPLE_CONFIG_DATA),
    File("tasks.json", SAMPLE_TASKS_DATA),
    File("contracts.json", SAMPLE_CONTRACTS_DATA),
    File(".gitignore", GITIGNORE_CONTENT, optional=True, warning=GITIGNORE_WARNING)
]


def initialize_project():
    tree = Tree(TREE)
    tree.create()
        