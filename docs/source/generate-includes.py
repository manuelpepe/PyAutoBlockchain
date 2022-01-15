#!python3
from pathlib import Path
from pab.config import SCHEMA
from projectutils.config import generate_docs


SOURCE_DIR = Path(__file__).parent.absolute()


def create_all_config_files():
    outfile = SOURCE_DIR / "all_configs.inc"
    with outfile.open("w") as fp:
        fp.write(generate_docs(SCHEMA))


if __name__ == "__main__":
    create_all_config_files()
