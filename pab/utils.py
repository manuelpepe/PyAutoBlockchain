import inspect
import json
import warnings

from pathlib import Path

from pab.strategy import BaseStrategy


def print_strats(print_params):
    print("Available strategies:")
    strats = json_strats()
    for strat, params in strats.items():
        print(f"* {strat}{':' if print_params else ''}")
        if print_params:
            for param in params:
                print(f"\t- {param}")
    if not print_params:
        print("use -v to see strategy parameters")


def json_strats():
    NOSHOW = ["blockchain", "name"]
    return {
        strat.__name__: {
            "params": [
                str(param) for name, param in
                inspect.signature(strat).parameters.items()
                if name not in NOSHOW
            ],
            "doc": strat.__doc__
        } 
        for strat in BaseStrategy.__subclasses__()
    }


class KeyfileOverrideException(Exception): pass


UNIT_MULTIPLIER = 1000000000000000000


def amountToDecimal(amount: int, decimals: int = 18) -> float:
    return amount / 10 ** decimals


def amountToPZAP(amount: int) -> str:
    warnings.warn(
        "amountToPZAP will be deprecated in version 0.4, use amountToDecimal instead",
        PendingDeprecationWarning
    )
    return f"{amount / UNIT_MULTIPLIER:.8f}"


def amountToWBTC(amount: int) -> str:
    warnings.warn(
        "amountToWBTC will be deprecated in version 0.4, use amountToDecimal instead",
        PendingDeprecationWarning
    )
    return f"{amount / 100000000:.8f}"


def amountToLPs(amount: int) -> str:
    warnings.warn(
        "amountToLPs will be deprecated in version 0.4, use amountToDecimal instead",
        PendingDeprecationWarning
    )
    return f"{amount / UNIT_MULTIPLIER:.25f}"


def PZAPToAmount(pzap: str) -> int:
    warnings.warn(
        "PZAPToAmount will be deprecated in version 0.4, use amountToDecimal instead",
        PendingDeprecationWarning
    )
    return int(float(pzap) * UNIT_MULTIPLIER)


def create_keyfile(path: Path, private_key: str, password: str):
    from web3 import Web3
    if path.is_file():
        raise KeyfileOverrideException("Warning, trying to overwrite existing keyfile")
    keydata = Web3().eth.account.encrypt(private_key, password)
    with path.open("w") as fp:
        json.dump(keydata, fp)