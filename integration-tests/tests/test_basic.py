import os

from pathlib import Path


def test_polygon(test_project):
    with test_project("Polygon") as root:
        print(os.listdir(root))
        contracts_file = root / "contracts.json"
        print(contracts_file.open("r").read())
    