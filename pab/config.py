import os
import json
import difflib

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from pathlib import Path

from dotenv import load_dotenv


DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

RESOURCES_DIR = Path(__file__).parent / Path("resources")
DEFAULTS_SCHEMA_FILE = RESOURCES_DIR / "config.schema.json" 

ABIS_DIR = Path("abis")
CONFIG_FILE = Path("config.json")
TASKS_FILE = Path("tasks.json")
CONTRACTS_FILE = Path("contracts.json")


class LCDict(dict):
    """ Lowercase dictionary for case-insensitive config names. """
    def __setitem__(self, key: str, value: Any) -> None:
        return super().__setitem__(key.lower(), value)

    def __getitem__(self, key: str):
        return super().__getitem__(key.lower())
    

def flatten(dict_: dict, base_path: str = '') -> dict:
    out = {}
    for key, value in dict_.items():
        cur_path = base_path + '.' + key
        cur_path = cur_path.strip('.')
        if isinstance(value, dict):
            out |= flatten(value, cur_path)
        else:
            out[cur_path] = value
    return out


class ConfigSource(ABC):
    """ Children of ConfigSource should implement `_load_data()` returning a 
    1-dimensional mapping of `path: value`. """
    def __init__(self):
        self.data = self._load_data()
    
    def items(self):
        return self.data.items()

    @abstractmethod
    def _load_data(self) -> Dict[str, Any]:
        """ Must return a dict of `path: value` mappings. """
        pass


class JSONSource(ConfigSource):
    """ Loads configs from `config.json` file. """
    def __init__(self, root: Path):
        self.file = root / CONFIG_FILE
        super().__init__()
    
    def _load_data(self) -> Dict[str, Any]:
        if not self.file.is_file():
            return {}
        with self.file.open('r') as fp:
            data = json.load(fp)
        return flatten(data)


class ENVSource(ConfigSource):
    """ Loads `.env` files and parses configs from environment. """
    PREFIX = "PAB_CONF_"

    def __init__(self, root: Path, envs: Optional[List[str]] = None):
        self.root = root
        self.envs = set(envs or [])
        self.base_envfile = root / '.env'
        super().__init__()
    
    def _load_data(self) -> Dict[str, Any]:
        if self.base_envfile.is_file():
            load_dotenv(self.base_envfile)
        for env in self.envs:
            envfile = self.root / f".env.{env}"
            if not envfile.is_file():
                raise FileNotFoundError(str(envfile))
            load_dotenv(envfile)
        return self._parse_environ()
        
    def _parse_environ(self) -> dict:
        output = {}
        for name, value in os.environ.items():
            if name.startswith(ENVSource.PREFIX):
                cname = self._get_config_name(name)
                output[cname] = value
        return output

    def _get_config_name(self, name: str) -> str:
        name = name.replace(ENVSource.PREFIX, '')
        return name.replace('_', '.')


def _list_formatter(value):
    if isinstance(value, str):
        return value.split(',')
    elif isinstance(value, list):
        return value
    raise InvalidConfigValue("Invalid value for list.")


def _bool_formatter(value):
    if isinstance(value, str):
        value = value.lower()
        if value in ('1', '0', 'true', 'false'):
            return value in ('1', 'true')
        raise InvalidConfigValue("Invalid value for bool. Accepted string values are: 1, 0, true, false")
    return bool(value)


FORMATTERS = {
    "int": int,
    "string": str,
    "float": float,
    "bool": _bool_formatter,
    "list": _list_formatter,
}


def _closest_formatter(format: str):
    out = 0, None
    for option in FORMATTERS.keys():
        ratio = difflib.SequenceMatcher(None, format, option).ratio()
        if ratio > out[0]:
            out = ratio, option
    return out[1]


def _get_formatter(format: str):
    if format in FORMATTERS.keys():
        return FORMATTERS[format]
    closest = _closest_formatter(format)
    hint = f" Did you mean '{closest}'?" if closest else ""
    raise ValueError(f"Invalid config formatter: '{format}'.{hint}")


class ConfigDef:
    def __init__(self, path: str, doc: str, format: str, default: Any):
        self.path = path
        self.doc = doc
        self.format = _get_formatter(format)
        self.default = default


class ConfigSchema:
    """ Loads default schema. `schema` is a mapping of `path: ConfigDef`. """
    def __init__(self):
        self.schema: LCDict = self._load()

    def __getitem__(self, path: str) -> Any:
        if path in self.schema.keys():
            return self.schema[path]
        raise ConfigNotDefined(f"'{path}' not defined in the config schema.")

    def _load(self) -> LCDict[str, ConfigDef]:
        output = LCDict()
        data = json.loads(DEFAULTS_SCHEMA_FILE.read_text())
        for path, definition in data.items():
            output[path] = ConfigDef(path=path, **definition)
        return output

    def format_value(self, path: str, value: Any) -> Any:
        return self.schema[path].format(value)

    def keys(self):
        return self.schema.keys()
    
    def items(self):
        return self.schema.items()

    def defaults(self):
        defaults = {}
        for path, def_ in self.items():
            _add_path_to_tree(defaults, path, def_.default)
        return defaults


def _merge_sources_and_format(schema: ConfigSchema, sources: List[ConfigSource]) -> LCDict:
    data = LCDict()
    for config in sources:
        for path, value in config.items():
            formatted = schema.format_value(path, value)
            data[path.lower()] = formatted
    return data


def _add_path_to_tree(tree: dict, path: str, value: Any):
    curnode = tree
    parts = path.split('.')
    for part in parts[:-1]:
        curnode = curnode.setdefault(part, {})
    curnode[parts[-1]] = value
    return tree


class Config:
    """ Readonly config interface. Loads and merges config data from multiple sources."""
    def __init__(self, root: Path, envs: Optional[List[str]] = None):
        self.root = root
        self.envs = envs
        self.schema = ConfigSchema()
        self.data: LCDict = LCDict()

    def load(self):
        self.data: LCDict = _merge_sources_and_format(self.schema,
            [
                JSONSource(self.root),
                ENVSource(self.root, self.envs)
            ]
        )
        return self
    
    def get(self, path: str):
        path = path.lower()
        if path in self.data.keys():
            return self.data[path]
        if any((name.startswith(path) and name != path for name in self.schema.keys())):
            return self._get_tree(path)
        return self.schema[path].default
     
    def _get_tree(self, path: str):
        tree = {}
        for name, def_ in self.schema.items():
            if name.startswith(path):
                value = self.data.get(name, def_.default)
                subpath = name[len(path) + 1:]  # +1 accounts for last '.'
                tree = _add_path_to_tree(tree, subpath, value)
        return tree


def load_configs(root: Path, envs: Optional[List[str]] = None):
    return Config(root, envs).load()


class InvalidConfigValue(ValueError):
    pass

class ConfigNotDefined(ValueError):
    pass
