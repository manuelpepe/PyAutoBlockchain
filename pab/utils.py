import json
import warnings

from pathlib import Path

from pab.config import APP_CONFIG
from pab.blockchain import Blockchain


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
    if path.is_file():
        raise KeyfileOverrideException("Warning, trying to overwrite existing keyfile")
    blockchain = Blockchain(APP_CONFIG.get('endpoint'), int(APP_CONFIG.get("chainId")), APP_CONFIG.get("blockchain"))
    keydata = blockchain.w3.eth.account.encrypt(private_key, password)
    with path.open("w") as fp:
        json.dump(keydata, fp)