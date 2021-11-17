from pab.queue import Queue, QueueItem, QueueLoader
from pab.strategy import import_strategies


def test_queue_loader_creation(blockchain):
    import_strategies(blockchain.root)
    queueloader = QueueLoader(blockchain)
    assert queueloader


def test_queue_loader_loads(blockchain):
    import_strategies(blockchain.root)
    queue = QueueLoader(blockchain).load()
    assert isinstance(queue, Queue)
    assert len(queue) > 0
    assert all(isinstance(item, QueueItem) for item in queue)
