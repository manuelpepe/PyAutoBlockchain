import re
import os
import json
import getpass
import logging

from typing import Dict, Optional
from pathlib import Path

from eth_account.account import Account, LocalAccount


_logger = logging.getLogger("pab.accounts")

ENVS_PREFIX = re.compile(r"^PAB_PK([0-9]*)")



def create_keyfile(path: Path, private_key: str, password: str) -> None:
    """ Creates a keyfile using :ref:`Web3.eth.account.encrypt`. """
    from web3 import Web3
    if path.is_file():
        raise KeyfileOverrideException("Warning, trying to overwrite existing keyfile")
    keydata = Web3().eth.account.encrypt(private_key, password)
    with path.open("w") as fp:
        json.dump(keydata, fp)


def _load_keyfile(keyfile: Path) -> Optional[LocalAccount]:
    """ Loads accounts from keyfile. Asks for user input. """
    if keyfile is None or not keyfile.is_file():
        _logger.warning(f"Keyfile at '{keyfile}' not found.")
        return
    with open(keyfile) as fp:
        wallet_pass = getpass.getpass(f"Enter {keyfile} password: ")
        return Account.from_key(Account.decrypt(json.load(fp), wallet_pass))


def _get_ix_from_name(name) -> Optional[int]:
    """ Returns the index from `PAB_PK<INDEX>`. """
    match = re.findall(ENVS_PREFIX, name)
    if match:
        return int(match[0])
    return None


def _load_from_env() -> Dict[int, LocalAccount]:
    """ Private keys are loaded from the environment variables that follow the naming
    convention `PAB_PK<ix>`. `ix` will be the index in the accounts list. """
    accounts = {}
    for name, value in os.environ.items():
        acc_ix = _get_ix_from_name(name)
        if acc_ix is not None:
            accounts[acc_ix] = Account.from_key(value)
    return accounts


def load_accounts(keyfiles: list[Path]) -> Dict[int, LocalAccount]:
    """ Load accounts from environment variables and keyfiles"""
    accounts = {}
    for keyfile in keyfiles:
        acc = _load_keyfile(keyfile)
        if acc is not None:
            accounts[len(accounts.keys())] = acc
    for ix, acc in _load_from_env().items():
        if ix in accounts.keys():
            raise AccountsError(f"Account index {ix} already used.")
        accounts[ix] = acc
    return accounts


class AccountsError(Exception):
    pass


class KeyfileOverrideException(Exception): 
    pass
