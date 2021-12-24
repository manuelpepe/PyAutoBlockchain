import inspect

from pab.strategy import BaseStrategy


def amountToDecimal(amount: int, decimals: int = 18) -> float:
    """ Available for strategies to convert between integers and decimal values. """
    return amount / 10 ** decimals


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
