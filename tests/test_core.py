from datetime import datetime, timedelta
from unittest.mock import MagicMock

from pab.strategy import BaseStrategy, SpecificTimeRescheduleError
from pab.core import PAB
from pab.task import TaskList, Task

RANDOM_DELTA = timedelta(hours=4)
RANDOM_DATE = datetime.now() + RANDOM_DELTA


class HarvestNotAvailable(SpecificTimeRescheduleError): 
    """ Harvest wasn't available. Should retry when it unlocks. """
    pass


class StrategyTestHarvestNotAvailable(BaseStrategy):
    def run(self):
        raise HarvestNotAvailable("TEST", RANDOM_DATE.timestamp())


class StrategyTestWorks(BaseStrategy):
    def run(self):
        return True


def test_item_runs(blockchain):
    strat = StrategyTestHarvestNotAvailable(None, "Test Strategy")
    strat.run = MagicMock(name="run")
    item = Task(0, strat, Task.RUN_ASAP)
    pab = PAB(blockchain.root)
    pab.tasks = TaskList([item])
    assert len(pab.tasks) == 1
    pab.process_tasks()
    strat.run.assert_called_once()


def test_that_fails_is_rescheduled(blockchain):
    strat = StrategyTestHarvestNotAvailable(None, "Test Strategy")
    item = Task(0, strat, Task.RUN_ASAP)
    pab = PAB(blockchain.root)
    pab.tasks = TaskList([item])
    pab.process_tasks()
    assert pab.tasks[0].next_at == int(RANDOM_DATE.timestamp())
    # Should wait RANDOM_DELTA before calling strat.run again
    strat.run = MagicMock(name="run")
    pab.process_tasks()
    strat.run.assert_not_called()
    # If we change the next_at time it should process it
    some_passed_date = (datetime.now() - timedelta(days=1)).timestamp()
    pab.tasks[0].schedule_for(int(some_passed_date))
    pab.process_tasks()
    strat.run.assert_called_once()


def test_failed_strategy_reschedules_using_repeat_every(blockchain):
    strat = StrategyTestWorks(None, "Test Strategy that works")
    item = Task(0, strat, Task.RUN_ASAP, repeat_every={"days": 1, "hours": 1})
    pab = PAB(blockchain.root)
    pab.tasks = TaskList([item])
    pab.process_tasks()
    item_next_exec = datetime.fromtimestamp(pab.tasks[0].next_at)
    difference_in_time = item_next_exec - datetime.now()
    assert difference_in_time > timedelta(days=1) and difference_in_time < timedelta(days=1, hours=1, seconds=1)
