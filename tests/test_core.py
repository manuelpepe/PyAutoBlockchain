from datetime import datetime, timedelta
from unittest.mock import MagicMock

from pab.strategy import BaseStrategy, SpecificTimeRescheduleError
from pab.core import PAB, TasksRunner, SingleStrategyRunner
from pab.task import TaskList, Task

RANDOM_DELTA = timedelta(hours=4)
RANDOM_DATE = datetime.now() + RANDOM_DELTA


class HarvestNotAvailable(SpecificTimeRescheduleError):
    """Harvest wasn't available. Should retry when it unlocks."""

    pass


class StrategyTestHarvestNotAvailable(BaseStrategy):
    def run(self):
        raise HarvestNotAvailable("TEST", RANDOM_DATE.timestamp())


class StrategyTestWorks(BaseStrategy):
    def run(self):
        return True


class StrategyTestWithParams(BaseStrategy):
    def __init__(self, *args, text: str, value: int):
        super().__init__(*args)
        self.text = text
        self.value = value

    def run(self):
        return True


def test_run_single(blockchain):
    pab = PAB(blockchain.root)
    runner = SingleStrategyRunner(pab, strategy="StrategyTestWorks", params=[])
    assert isinstance(runner.strat, StrategyTestWorks)
    runner.strat.run = MagicMock(name="run")
    runner.run()
    runner.strat.run.assert_called_once()


def test_run_single_with_params(blockchain):
    pab = PAB(blockchain.root)
    runner = SingleStrategyRunner(
        pab,
        strategy="StrategyTestWithParams",
        params=["--text", "asd", "--value", "123"],
    )
    assert isinstance(runner.strat, StrategyTestWithParams)
    assert isinstance(runner.strat.text, str)
    assert isinstance(runner.strat.value, int)
    runner.strat.run = MagicMock(name="run")
    runner.run()
    runner.strat.run.assert_called_once()


def test_task_runs(blockchain):
    strat = StrategyTestHarvestNotAvailable(None, "Test Strategy")
    strat.run = MagicMock(name="run")
    item = Task(0, strat, Task.RUN_ASAP)
    pab = PAB(blockchain.root)
    runner = TasksRunner(pab)
    runner.tasks = TaskList([item])
    assert len(runner.tasks) == 1
    runner.process_tasks()
    strat.run.assert_called_once()


def test_task_fails_is_rescheduled(blockchain):
    strat = StrategyTestHarvestNotAvailable(None, "Test Strategy")
    item = Task(0, strat, Task.RUN_ASAP)
    pab = PAB(blockchain.root)
    runner = TasksRunner(pab)
    runner.tasks = TaskList([item])
    runner.process_tasks()
    assert runner.tasks[0].next_at == int(RANDOM_DATE.timestamp())
    # Should wait RANDOM_DELTA before calling strat.run again
    strat.run = MagicMock(name="run")
    runner.process_tasks()
    strat.run.assert_not_called()
    # If we change the next_at time it should process it
    some_passed_date = (datetime.now() - timedelta(days=1)).timestamp()
    runner.tasks[0].schedule_for(int(some_passed_date))
    runner.process_tasks()
    strat.run.assert_called_once()


def test_task_repeats(blockchain):
    strat = StrategyTestWorks(None, "Test Strategy that works")
    item = Task(0, strat, Task.RUN_ASAP, repeat_every={"days": 1, "hours": 1})
    pab = PAB(blockchain.root)
    runner = TasksRunner(pab)
    runner.tasks = TaskList([item])
    runner.process_tasks()
    item_next_exec = datetime.fromtimestamp(runner.tasks[0].next_at)
    difference_in_time = item_next_exec - datetime.now()
    assert difference_in_time > timedelta(days=1) and difference_in_time < timedelta(
        days=1, hours=1, seconds=1
    )
