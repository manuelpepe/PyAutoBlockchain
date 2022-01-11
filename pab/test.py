from __future__ import annotations
from enum import Enum

import subprocess
import shutil
import json
import re
import os

from pathlib import Path
from contextlib import contextmanager
from tempfile import TemporaryDirectory
from dataclasses import dataclass

import pytest

from pab.core import PAB
from pab.strategy import BaseStrategy
from pab.init import chdir


def log(msg: str):
    """Print message to screen during pytest execution."""
    print(f"PABPlugin: {msg}")


def pytest_addoption(parser):
    parser.addini(
        "pab-contracts-sources",
        type="linelist",
        help="each line specifies a directory relative to the project root "
        "where a truffle project can be found",
        default=["tests/truffle"],
    )
    parser.addini(
        "pab-ignore-patterns-on-copy",
        type="linelist",
        help="each line specifies a directory relative to the project root "
        "that will not be copied when running 'setup_project'. This can speed "
        "up test executions by avoiding copying directories like 'venv'.",
        default=["venv"],
    )
    parser.addini(
        "pab-truffle-network",
        type="string",
        help="value for truffle --network parameter",
        default="development",
    )


def pytest_configure(config):
    config._pab = PABPlugin(config)
    config.pluginmanager.register(config._pab)


def _check_dependencies_installed(commands: list[str]) -> None:
    """Checks if a list of commands are available on the system usin :ref:`shutil.which`."""
    missing = []
    for cmd in commands:
        if shutil.which(cmd) is None:
            missing.append(cmd)
    if missing:
        raise PABTestException(f"Missing dependencies: {', '.join(missing)}.")


@dataclass
class ParsedGanacheOutput:
    """Dataclass for ganache data."""

    accounts: list[str]
    endpoint: str


def _parse_ganache_output(proc: subprocess.Popen) -> ParsedGanacheOutput:
    """Parses ganache process stdout for accounts and endpoint."""
    STOP_SEARCH_RE = re.compile(r"Listening on ([0-9\.:]*)")
    endpoint = ""
    data = ""
    while True:
        for chunk in proc.stdout.readline():
            print(chunk, end="")
            data += chunk
        if m := re.search(STOP_SEARCH_RE, data):
            endpoint = m.group(1)
            break
        if proc.poll() is not None:
            raise RuntimeError("Ganache terminated unexpectedly")
    return ParsedGanacheOutput(
        accounts=re.findall(r"\([0-9]\) (0x[a-zA-Z0-9]{64})", data), endpoint=endpoint
    )


class PABPlugin:
    """
    This plugin will:

        * Verify that `ganache-cli` and `truffle` are installed.
        * Start a `ganache-cli` subprocess.
        * Collect the private keys of all test accounts in the local ganache network.
        * Build and deploy your contracts with `truffle` into the local ganache network.
        * Collect the addresses of the deployed contracts.
        * Install fixtures
    """

    GANACHE_CMD = "ganache-cli"
    TRUFFLE_CMD = "truffle"

    def __init__(self, config):
        self.config = config
        self._ganache_proc: subprocess.Popen | None = None
        self.accounts: list[str] = []
        self.contracts: dict[str, Contract] = {}
        self.envs: dict[str, str] = {}
        self._truffle_network: str = config.getini("pab-truffle-network")
        self._contracts_sources: list[str] = config.getini("pab-contracts-sources")
        self.ignored_patterns: list[str] = config.getini("pab-ignore-patterns-on-copy")

    def pytest_sessionstart(self, session):
        """Pytest start hook"""
        _check_dependencies_installed([self.TRUFFLE_CMD, self.GANACHE_CMD])
        log("Starting ganache-cli server...")
        self._start_ganache_process()
        self._collect_ganache_data()
        log("Deploying contracts with truffle...")
        self._deploy_contracts_with_truffle()
        log("Done")

    def pytest_sessionfinish(self, session, exitstatus):
        """Pytest cleanup hook"""
        if self._ganache_proc:
            log("Stopping ganache-cli server")
            self._ganache_proc.kill()

    def _start_ganache_process(self):
        """Starts ganache-cli process."""
        self._ganache_proc = subprocess.Popen(
            [self.GANACHE_CMD],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf8",
        )

    def _collect_ganache_data(self):
        """Parses ganache process output and collects accounts and network data."""
        if not self._ganache_proc:
            raise RuntimeError("Ganache process not found.")
        parsed = _parse_ganache_output(self._ganache_proc)
        self.accounts = parsed.accounts
        self.envs["PAB_CONF_ENDPOINT"] = f"http://{parsed.endpoint}/"
        self.envs["PAB_CONF_CHAINID"] = "1337"
        self.envs["PAB_CONF_BLOCKCHAIN"] = "Ganache"
        if not self.accounts:
            raise RuntimeError("No accounts were loaded from Ganache.")

    def _deploy_contracts_with_truffle(self):
        """Test, build and deploy contracts with ganache."""
        deployer = TruffleDeployer(self._contracts_sources, self._truffle_network)
        self.contracts = deployer.deploy()


@dataclass
class Contract:
    name: str
    source: str
    address: str
    abi: str


class TruffleDeployer:
    CMD = "truffle"

    def __init__(self, sources: list[str], network: str):
        self.sources: list[str] = sources
        self.network: str = network

    def deploy(self) -> dict[str, Contract]:
        """Spawns a truffle deploy process for each source, parses process
        output and returns a mapping of `contract_name: Contract`."""
        data_by_source: dict[str, dict] = {}
        for source in self.sources:
            path = str(Path(source).absolute())
            proc = self._run_truffle(path)
            parser = TruffleOutputParser()
            data_by_source[source] = parser.parse_contracts_data(proc)
        return self._parse_data_and_validate(data_by_source)

    def _run_truffle(self, cwd: str):
        return subprocess.run(
            [self.CMD, "deploy", "--network", self.network],
            capture_output=True,
            cwd=cwd,
            encoding="utf8",
        )

    def _parse_data_and_validate(
        self, sources_data: dict[str, dict]
    ) -> dict[str, Contract]:
        output: dict[str, Contract] = {}
        for source, contracts in sources_data.items():
            for name, data in contracts.items():
                if name in output.keys():
                    prev_source = output[name].source
                    raise RuntimeError(
                        f"Contract with name '{name}' was deployed multiple times ({source}, {prev_source})"
                        "PAB does not currently support multiple contracts with the same name."
                    )
                output[name] = Contract(name, source, data["contract address"], "")
        return self._load_abis(output)

    def _load_abis(self, contracts: dict[str, Contract]) -> dict[str, Contract]:
        """Load the contract ABIs from the truffle sources 'build' directory."""
        for name, data in contracts.items():
            metadata_path = Path(data.source, "build/contracts", f"{name}.json")
            metadata = json.loads(metadata_path.read_text())
            data.abi = metadata["abi"]
        return contracts


class TruffleOutputParser:
    """Parser for truffle output. Currently only supports the deploy process and returns
    a mapping of `contract_name: contract_data`."""

    RE_START_CONTRACT = re.compile(r"^(Deploying|Replacing) '(.*)'$")
    RE_CONTRACT_DATA = re.compile(r"^> ([a-zA-Z ]+):\s+(.*)$")

    class States(Enum):
        START_CONTRACT_DATA = 1
        IN_CONTRACT_DATA = 2
        END_CONTRACT_DATA = 3
        OUTSIDE_CONTRACT_DATA = 4

    def __init__(self) -> None:
        self.state = self.States.OUTSIDE_CONTRACT_DATA

    def in_state(self, states: States | list[States]):
        if not isinstance(states, list):
            states = [states]
        return any(self.state == s for s in states)

    def parse_contracts_data(
        self, proc: subprocess.CompletedProcess
    ) -> dict[str, dict]:
        """Parses subprocess output. Returns a mapping of `contract_name: contract_data`."""
        lines = (ln.strip() for ln in proc.stdout.split("\n"))
        contracts = {}
        cur_contract = None
        for line in lines:
            print(line)
            if (match := re.match(self.RE_START_CONTRACT, line)) and self.in_state(
                self.States.OUTSIDE_CONTRACT_DATA
            ):
                cur_contract = match.group(2)
                if cur_contract in contracts.keys():
                    raise RuntimeError("Contract with same name deployed twice.")
                contracts[cur_contract] = {}
                self.state = self.States.IN_CONTRACT_DATA
            elif (match := re.match(self.RE_CONTRACT_DATA, line)) and self.in_state(
                self.States.IN_CONTRACT_DATA
            ):
                key, value = match.group(1), match.group(2)
                contracts[cur_contract][key] = value
            elif line == "" and self.in_state(self.States.IN_CONTRACT_DATA):
                cur_contract = None
                self.state = self.States.END_CONTRACT_DATA
            elif line == "" and self.in_state(self.States.END_CONTRACT_DATA):
                self.state = self.States.OUTSIDE_CONTRACT_DATA
        return contracts


def _copy_project(dest: Path, ignored_patterns: list[str] | None = None) -> Path:
    """Copies CWD to `dest`."""
    if ignored_patterns is None:
        ignored_patterns = []
    dest = dest / "project"
    shutil.copytree(
        Path().absolute(), dest, ignore=shutil.ignore_patterns(*ignored_patterns)
    )
    return dest


def _set_test_envfile(path: Path, extra_vars: dict[str, str], plugin: PABPlugin):
    """Creates '.env.test' file in `path`. `extra_vars` is a dict of envvars to add to the file.
    Also adds envvars from `plugin.envs` and accounts from `plugin.accounts`."""
    envfile = path / ".env.test"
    data = ""
    if extra_vars:
        data += "\n".join(f'{k}="{v}"' for k, v in extra_vars.items()) + "\n"
    if plugin.envs:
        data += "\n".join(f'{k}="{v}"' for k, v in plugin.envs.items()) + "\n"
    if plugin.accounts:
        data += (
            "\n".join(f'PAB_PK{i}="{v}"' for i, v in enumerate(plugin.accounts)) + "\n"
        )
    envfile.write_text(data)


def _replace_contracts(pab: PAB, plugin: PABPlugin):
    """Replaces contracts in a PAB instance with the ones from `plugin.contracts`."""
    from pab.contract import ContractData

    for name, contract in plugin.contracts.items():
        pab.blockchain.contracts.contracts[name] = ContractData(
            name, contract.address, contract.abi
        )


@contextmanager
def _temp_environ():
    """ContextManager that Saves a copy of the environment
    and restores the environment variables to their original state after exiting.
    New variables will be removed and value changes will be undone."""
    prev_environ = os.environ.copy()
    yield
    os.environ.clear()
    os.environ.update(prev_environ)


@pytest.fixture
def setup_project(pytestconfig):
    """This fixture will:

    * Copy project to a temporary directory.
    * Change CWD to temporary directory.
    * Replace the contract adresses loaded from contracts.json with the local addresses.
    * Create a '.env.test' environment file with local accounts and rpc configs.
    * Restore environment variables after execution.
    * Return a PAB instance.
    """

    @contextmanager
    def _setup_project(env_data: dict[str, str] = None):
        if env_data is None:
            env_data = {}
        with TemporaryDirectory() as tmpdir:
            project_path = _copy_project(
                Path(tmpdir), pytestconfig._pab.ignored_patterns
            )
            _set_test_envfile(project_path, env_data, pytestconfig._pab)
            pab = PAB(project_path, envs=["test"], load_tasks=False)
            _replace_contracts(pab, pytestconfig._pab)
            with _temp_environ():
                with chdir(project_path):
                    yield pab

    return _setup_project


@pytest.fixture
def get_strat():
    """Fixture that returns an initialized strategy from a PAB instance."""

    def _get_strat(pab: PAB, strat_name: str, params: dict) -> BaseStrategy:
        strat_class = pab.strategies.get(strat_name)
        if strat_class is None:
            raise StrategyNotFound("Strategy not found")
        return strat_class(pab.blockchain, f"Test-{strat_name}", **params)

    return _get_strat


class PABTestException(Exception):
    ...


class MissingDependencies(PABTestException):
    ...


class StrategyNotFound(PABTestException):
    ...
