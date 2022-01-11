import typing
from pathlib import Path


if typing.TYPE_CHECKING:
    from ..strategies import CompoundAndLog


def test_compounds_and_log(setup_project, get_strat, pytestconfig):
    with setup_project() as pab:
        outfile = Path("/tmp/test.txt")
        params = {
            "filepath": str(outfile),
            "token": "Token",
            "controller": "Controller",
            "account_index": 1,
        }
        strat: "CompoundAndLog" = get_strat(pab, "CompoundAndLog", params)
        account, controller = strat.account, strat.controller
        # we start with balance 0
        assert (
            controller.functions.getBalance(account.address, strat.pool_id).call() == 0
        )
        # stake 10 and check balance
        strat.transact(account, controller.functions.stake, (strat.pool_id, 10))
        assert (
            controller.functions.getBalance(account.address, strat.pool_id).call() == 10
        )
        # and after the strategy compounds balance should be 20
        strat.run()
        assert (
            controller.functions.getBalance(account.address, strat.pool_id).call() == 20
        )
        # also check log was generated correctly
        assert outfile.read_text().strip() == "10,20,10"
