from pab.queue import Queue, Job, QueueLoader
from pab.strategy import load_strategies


def test_queue_loader_creation(blockchain):
    strats = load_strategies(blockchain.root)
    queueloader = QueueLoader(blockchain, strats)
    assert queueloader


def test_queue_loader_loads(blockchain):
    strats = load_strategies(blockchain.root)
    queue = QueueLoader(blockchain, strats).load()
    assert isinstance(queue, Queue)
    assert len(queue) > 0
    assert all(isinstance(item, Job) for item in queue)
