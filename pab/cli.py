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

from pab.core import PAB, TasksRunner, SingleStrategyRunner
from pab.config import DATETIME_FORMAT, Config
from pab.strategy import import_strategies
from pab.utils import print_strats, json_strats
from pab.alert import alert_exception
from pab.init import initialize_project as _initialize_project
from pab.accounts import create_keyfile, KeyfileOverrideException


def _create_logger():
    fhandler = logging.FileHandler("pab.log", "a", "utf-8")
    fhandler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s - %(message)s", datefmt=DATETIME_FORMAT
        )
    )

    shandler = logging.StreamHandler(sys.stdout)
    shandler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))

    logger = logging.getLogger()
    logger.addHandler(shandler)
    logger.addHandler(fhandler)
    logger.setLevel(logging.INFO)
    return logger


def _create_keyfile(args, extra, logger):
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


def list_strats(args, extra, logger):
    import_strategies(Path.cwd())
    if args.json:
        json.dump(json_strats(), sys.stdout)
        print()
    else:
        print_strats(args.verbose)


def initialize_project(args, extra, logger):
    directory = args.directory
    if directory is None:
        directory = Path.cwd()
    _initialize_project(directory)


def _parse_run_args(args) -> tuple:
    envs = [env.strip() for env in args.envs.split(",") if env.strip() != ""]
    keyfiles = [kf.strip() for kf in args.keyfiles.split(",") if kf.strip() != ""]
    keyfiles_paths = [Path(kf) for kf in keyfiles]
    return envs, keyfiles_paths


def run_tasks(args, extra, logger):
    envs, keyfiles = _parse_run_args(args)
    pab = PAB(Path.cwd(), keyfiles, envs)
    runner = TasksRunner(pab)
    sys.excepthook = exception_handler(logger, pab.config)
    runner.run()


def run_strat(args, extra, logger):
    envs, keyfiles = _parse_run_args(args)
    pab = PAB(Path.cwd(), keyfiles, envs)
    runner = SingleStrategyRunner(pab, strategy=args.strategy, params=extra)
    sys.excepthook = exception_handler(logger, pab.config)
    runner.run()


def parser():
    p = ArgumentParser(
        "pab", description=__doc__, formatter_class=RawDescriptionHelpFormatter
    )
    subparsers = p.add_subparsers(help="subcommands for pab")

    p_create = subparsers.add_parser(
        "list-strategies", help="List strategies and parameters"
    )
    p_create.add_argument(
        "-v", "--verbose", action="store_true", help="Print strategy parameters"
    )
    p_create.add_argument(
        "-j", "--json", action="store_true", help="Print strategies as JSON"
    )
    p_create.set_defaults(func=list_strats)

    p_run = subparsers.add_parser("run", help="Run PAB")
    p_run.add_argument(
        "-k",
        "--keyfiles",
        action="store",
        help="List of keyfiles separated by commas.",
        default="",
    )
    p_run.add_argument(
        "-e", "--envs", help="List of environments separated by commas.", default=""
    )

    p_run_subparsers = p_run.add_subparsers(help="subcommands for pab run")
    p_run_tasks = p_run_subparsers.add_parser(
        "tasks", description="Run and schedule all tasks from 'tasks.json'."
    )
    p_run_tasks.set_defaults(func=run_tasks)

    p_run_strat = p_run_subparsers.add_parser(
        "strat", description="Run a single strategy by name."
    )
    p_run_strat.add_argument(
        "--strategy", type=str, help="Name of the strategy to run", required=True
    )
    p_run_strat.set_defaults(func=run_strat)

    p_createkf = subparsers.add_parser(
        "create-keyfile",
        help="Create keyfile. You'll need your private key and a new password for the keyfile.",
    )
    p_createkf.add_argument(
        "-o",
        "--output",
        action="store",
        help="Output location for keyfile.",
        default="key.file",
    )
    p_createkf.set_defaults(func=_create_keyfile)

    p_init = subparsers.add_parser(
        "init", help="Initialize PAB project in current directory."
    )
    p_init.add_argument(
        "-d",
        "--directory",
        action="store",
        help="Initialize project in diferent directory.",
        default=None,
    )
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
        logger.critical(
            "Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback)
        )
        alert_exception(exc_value, config)

    return _handle_exceptions


def main(args):
    logger = _create_logger()
    args, extra = parser().parse_known_args(args)
    if hasattr(args, "func"):
        with _catch_ctrlc():
            args.func(args, extra, logger)
    else:
        parser().print_help()


def ep():
    main(sys.argv[1:])


if __name__ == "__main__":
    ep()
