import os
import re
import toml
import pytest
import shutil

from tempfile import TemporaryDirectory
from contextlib import contextmanager
from pathlib import Path

from pab.core import PAB
from pab.init import chdir


@contextmanager
def temp_environ():
    prev_environ = {**os.environ}
    yield
    os.environ = prev_environ


def _load_envvars_mapping():
    """ ENVS are loaded from the file `integration-tests/envs.toml`. """
    envs_file = Path(__file__).parent / 'envs.toml'
    with envs_file.open('r') as fp:
        return toml.load(fp)


ENVS = _load_envvars_mapping()
DEV_CONTRACTS_FILE = Path(__file__).parent / ".contracts.map" 


def _copy_project(project_name: str, dest: Path) -> Path:
    project_path = Path(__file__).parent / "projects" / project_name
    dest_path = dest / project_name
    shutil.copytree(project_path, dest_path)
    return dest_path


def _parse_contracts_file() -> dict:
    if not DEV_CONTRACTS_FILE.is_file():
        raise RuntimeError(".contracts.map file not found.")
    contracts = {}
    with DEV_CONTRACTS_FILE.open("r") as fp:
        for line in fp.readlines():
            if not line.strip():
                continue
            name, address = line.split(":")
            contracts[name] = address
    return contracts


def _replace_contracts_in_data(contracts: dict, data: str) -> str:
    for name, address in contracts.items():
        data = data.replace(f"{{{name}}}", address.strip())
    unreplaced = re.findall(r"\"{([a-zA-Z0-9]*)}\"", data, re.MULTILINE)
    if unreplaced:
        raise RuntimeError(f"Couldn't replace addresses for contracts: {', '.join(unreplaced)}")
    return data


def _set_dev_contract_addresses(project_path: Path):
    contracts = _parse_contracts_file()
    project_contracts_file = project_path / "contracts.json"
    with project_contracts_file.open("r") as fp:
        data = _replace_contracts_in_data(contracts, fp.read())
    with project_contracts_file.open("w") as fp:
        fp.write(data)


def _set_envfile(project_path: Path, envs: dict):
    envfile = project_path / '.env'
    data = '\n'.join(f'{k}="{v}"' for k, v in envs.items())
    envfile.write_text(data)


@contextmanager
def _setup_project(project_name: str) -> PAB:
    with TemporaryDirectory() as tmpdir:
        project_path = _copy_project(project_name, Path(tmpdir))
        _set_dev_contract_addresses(project_path)
        _set_envfile(project_path, ENVS.get('GLOBAL', {}) | ENVS.get(project_name, {}))
        with temp_environ():
            with chdir(project_path):
                yield PAB(project_path)


@pytest.fixture
def setup_project() -> PAB:
    return _setup_project

