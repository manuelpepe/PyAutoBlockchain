import json
from json.decoder import JSONDecodeError

from typing import List, Any
from pathlib import Path

from pab.exceptions import MissingConfig


def valid_config_found():
    if CONFIG_FILE.is_file():
        try:
            with CONFIG_FILE.open("r") as fp:
                json.load(fp)
                return True
        except JSONDecodeError:
            pass
    return False


def override_config_with_defaults():
    with CONFIG_FILE.open("w") as fp:
        data = DEFAULTS_CONFIG_FILE.open("r").read()
        fp.write(data)


class MissingConfigFile(Exception):
    pass


class JSONConfig:
    def __init__(self, paths: List[Path]):
        self.paths = paths
        self.datas = self._read_datas()
    
    def _read_datas(self) -> List[dict]:
        out = []
        for path in self.paths:
            if path.is_file():
                with open(path, "r") as fp:
                    out.append(json.load(fp))
        return out
    
    def get(self, name) -> Any:
        """ Returns config value from `name`. """
        path = name.split(".")
        for data in self.datas:
            try:
                return self._get_dict_value_from_path(path, data)
            except NameError:
                pass
        raise MissingConfig(f"Could not find '{name}' in config.")

    def _get_dict_value_from_path(self, path: List[str], store: dict) -> Any:
        """ Tries to find the value for a given `path` in the `store` dictionary.
        Path can be a series of key names in the dictionary (e.g: `transaction.timeout`). 
        If any key can't be found it raises NameError. """
        current = store
        for key in path:
            if not isinstance(current, dict) or key not in current.keys():
                raise NameError(f"'{path}' not found.")
            current = current[key]
        return current

    def __getitem__(self, key):
        return self.get(key)


DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'


# Files and directories
RESOURCES_DIR = Path(__file__).parent / Path("resources")
DEFAULTS_CONFIG_FILE = RESOURCES_DIR / "config.defaults.json" 

ABIS_DIR = Path("abis")
CONFIG_FILE = Path("config.json")
TASKS_FILE = Path("tasks.json")
CONTRACTS_FILE = Path("contracts.json")
KEY_FILE = Path("key.file")


# Load config
if not CONFIG_FILE.is_file:
    raise MissingConfigFile("Please create a config.json in your cwd.")
    
try:
    APP_CONFIG = JSONConfig([CONFIG_FILE, DEFAULTS_CONFIG_FILE])
except Exception:
    APP_CONFIG = JSONConfig([DEFAULTS_CONFIG_FILE])

ENDPOINT = APP_CONFIG.get('endpoint')

