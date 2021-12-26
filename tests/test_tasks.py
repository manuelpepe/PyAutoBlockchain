from pab.task import TaskList, Task, TaskFileParser
from pab.strategy import load_strategies


def test_task_file_parser_creation(blockchain):
    strats = load_strategies(blockchain.root)
    parser = TaskFileParser(blockchain.root, blockchain, strats)
    assert parser


def test_task_file_parser_loads(blockchain):
    strats = load_strategies(blockchain.root)
    tasks = TaskFileParser(blockchain.root, blockchain, strats).load()
    assert isinstance(tasks, list)
    assert len(tasks) > 0
    assert all(isinstance(item, Task) for item in tasks)
