import json
from pathlib import Path

from pab.exceptions import MissingConfig


class MissingConfigFile(Exception):
    pass


class JSONConfig:
    def __init__(self, path: Path):
        self.path = path
        self.data = self._read_data()
    
    def _read_data(self):
        with open(self.path, "r") as fp:
            return json.load(fp)

    def __getitem__(self, key):
        return self.data[key]

    def get(self, key, default = None):
        return self.data.get(key, default)


DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'


# Files and directories

RESOURCES_DIR = Path(__file__).parent / Path("resources")
SAMPLE_CONFIG_FILE = RESOURCES_DIR / "config.sample.json" 

ABIS_DIR = Path("abis")
CONFIG_FILE = Path("config.json")
TASKS_FILE = Path("tasks.json")
CONTRACTS_FILE = Path("contracts.json")
KEY_FILE = Path("key.file")


# Load from config file

if CONFIG_FILE.is_file():
    APP_CONFIG = JSONConfig(CONFIG_FILE)
else:
    APP_CONFIG = {}

ENDPOINT = APP_CONFIG.get('endpoint', '')
MY_ADDRESS = APP_CONFIG.get('myAddress', '')

_EMAIL_CONFIG = APP_CONFIG.get("emails", {})

ALERTS_ON = _EMAIL_CONFIG.get("enabled", False)
ALERTS_HOST = _EMAIL_CONFIG.get("host", "localhost")
ALERTS_PORT = _EMAIL_CONFIG.get("port", 587)
ALERTS_ADDRESS = _EMAIL_CONFIG.get("address", None)
ALERTS_PASSWORD = _EMAIL_CONFIG.get("password", None)
ALERTS_RECIPIENT = _EMAIL_CONFIG.get("recipient", None)
