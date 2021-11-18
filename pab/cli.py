"""
PAB is a framework for developing and running custom tasks in crypto blockchains.
"""
import json
import os
import sys
import getpass
import logging

from pathlib import Path
from contextlib import contextmanager
from argparse import ArgumentParser, RawDescriptionHelpFormatter

from pab.core import PAB
from pab.config import DATETIME_FORMAT, KEY_FILE, Config
from pab.strategy import import_strategies
from pab.utils import create_keyfile, KeyfileOverrideException, print_strats, json_strats
from pab.alert import alert_exception
from pab.init import initialize_project as _initialize_project


def _create_logger():
    fhandler = logging.FileHandler("pab.log", "a", "utf-8")
    fhandler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s - %(message)s", datefmt=DATETIME_FORMAT))

    shandler = logging.StreamHandler(sys.stdout)
    shandler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))

    logger = logging.getLogger()
    logger.addHandler(shandler)
    logger.addHandler(fhandler)
    logger.setLevel(logging.INFO)
    return logger


def _create_keyfile(args, logger):
    private_key = getpass.getpass("Enter private key: ")
    password = getpass.getpass("Enter keyfile password: ")
    pass_repeat = getpass.getpass("Repeat keyfile password: ")
    if password != pass_repeat:
        logger.error("Passwords don't match")
        sys.exit(1)
    try:
        out = Path(args.output)
        create_keyfile(out, private_key, pass_repeat)
    except KeyfileOverrideException as err:
        logger.error(err)
        sys.exit(1)
    logger.info(f"Keyfile written to '{out}'")


def list_strats(args, logger):
    import_strategies(Path.cwd())
    if args.json:
        json.dump(json_strats(), sys.stdout)
        print()
    else:
        print_strats(args.verbose)


def initialize_project(args, logger):
    # TODO: handle args.directory
    _initialize_project()


def run(args, logger):
    pab = PAB(Path.cwd(), args.keyfile)
    sys.excepthook = exception_handler(logger, pab.config)
    pab.start()


def parser():
    p = ArgumentParser("pab", description=__doc__, formatter_class=RawDescriptionHelpFormatter)
    subparsers = p.add_subparsers(help="subcommands for pab")

    p_create = subparsers.add_parser("list-strategies", help="List strategies and parameters")
    p_create.add_argument("-v", "--verbose", action="store_true", help="Print strategy parameters")
    p_create.add_argument("-j", "--json", action="store_true", help="Print strategies as JSON")
    p_create.set_defaults(func=list_strats)

    p_run = subparsers.add_parser("run", help="Run tasks")
    p_run.add_argument("-k", "--keyfile", action="store", help="Wallet Encrypted Private Key. If not used will load from resources/key.file as default.", default=None)
    p_run.set_defaults(func=run)

    p_createkf = subparsers.add_parser("create-keyfile", help="Create keyfile. You'll need your private key and a new password for the keyfile.")
    p_createkf.add_argument("-o", "--output", action="store", help="Output location for keyfile.", default=str(KEY_FILE))
    p_createkf.set_defaults(func=_create_keyfile)

    p_init = subparsers.add_parser("init", help="Initialize PAB project in current directory.")
    p_createkf.add_argument("-d", "--directory", action="store", help="Initialize project in diferent directory.", default=str(KEY_FILE))
    p_init.set_defaults(func=initialize_project)
    return p


@contextmanager
def _catch_ctrlc():
    try:
        yield
    except KeyboardInterrupt:
        print("Ctrl+C")
        try:
            sys.exit(1)
        except SystemExit:
            os._exit(1)


def exception_handler(logger, config: Config):
    def _handle_exceptions(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
        alert_exception(exc_value, config)
    return _handle_exceptions


def main():
    logger = _create_logger()
    args = parser().parse_args()
    if hasattr(args, 'func'):
        with _catch_ctrlc():
            args.func(args, logger)
    else:
        parser().print_help()


if __name__ == "__main__":
    main()
