from __future__ import annotations

from pathlib import Path

from projectutils.config import Config, JSONSource, ENVSource, ConfigSchema


DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

RESOURCES_DIR = Path(__file__).parent / Path("resources")
DEFAULTS_SCHEMA_FILE = RESOURCES_DIR / "config.schema.json"

ABIS_DIR = Path("abis")
CONFIG_FILE = Path("config.json")
TASKS_FILE = Path("tasks.json")
CONTRACTS_FILE = Path("contracts.json")

ENV_VARS_PREFIX = "PAB_CONF_"

SCHEMA = ConfigSchema.from_json_file(DEFAULTS_SCHEMA_FILE)


def load_configs(root: Path, envs: list[str] | None = None):
    return Config(SCHEMA, [JSONSource(root), ENVSource(ENV_VARS_PREFIX, root, envs)])
