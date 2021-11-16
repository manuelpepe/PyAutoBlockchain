import re
import toml
import pytest
import shutil

from tempfile import TemporaryDirectory
from contextlib import contextmanager
from pathlib import Path

from pab.init import chdir


def _load_envvars_mapping():
    """ SECRETS are loaded from the file `integration-tests/.secrets.toml`.
    In that file you can specify Environment Variables for different Testing Projects 
    to override configs that need to contain sensitive data (such as address or email server)."""
    secrets_file = Path(__file__).parent / '.secrets.toml'
    with secrets_file.open('r') as fp:
        return toml.load(fp)


SECRETS = _load_envvars_mapping()
DEV_CONTRACTS_FILE = Path(__file__).parent / ".contracts.map" 


def _copy_project(project_name: str, dest: Path) -> Path:
    project_path = Path(__file__).parent / "projects" / project_name
    dest_path = dest / project_name
    shutil.copytree(project_path, dest_path)
    return dest_path


def _parse_contracts_file() -> dict:
    if not DEV_CONTRACTS_FILE.is_file():
        raise RuntimeError(".contracts file not found.")
    contracts = {}
    with DEV_CONTRACTS_FILE.open("r") as fp:
        for line in fp.readline():
            if not line.strip():
                continue
            name, address = line.split(":")
            contracts[name] = address
    return contracts


def _replace_contracts_in_data(contracts: dict, data: str) -> str:
    for name, address in contracts.items():
        data.replace(f"{{{name}}}", address)
    unrelaced = re.findall(r"\"{([a-zA-Z0-9]*)}\"", data, re.MULTILINE)
    if unrelaced:
        raise RuntimeError(f"Couldn't replace addresses for contracts: {', '.join(unrelaced)}")
    return data


def _set_dev_contract_addresses(project_path: Path):
    contracts = _parse_contracts_file()
    project_contracts_file = project_path / "contracts.json"
    with project_contracts_file.open("r") as fp:
        data = _replace_contracts_in_data(contracts, fp.read())
    with project_contracts_file.open("w") as fp:
        fp.write(data)
    

@contextmanager
def _setup_project(project_name: str) -> Path:
    with TemporaryDirectory() as tmpdir:
        project_path = _copy_project(project_name, Path(tmpdir))
        _set_dev_contract_addresses(project_path)
        with chdir(project_path):
            yield project_path


@pytest.fixture
def setup_project() -> Path:
    return _setup_project

