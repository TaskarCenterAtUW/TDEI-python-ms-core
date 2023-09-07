import unittest
from abc import ABC

from src.python_ms_core.core.queue.abstracts.queue_abstract import QueueAbstract


class TestQueueAbstract(unittest.TestCase):
    class ConcreteQueue(QueueAbstract):
        def __init__(self, config):
            super().__init__(config=config)

        def send(self, data=None):
            pass

        def add(self, data):
            pass

        def remove(self):
            pass

        def get_items(self):
            pass

    def test_concrete_queue_inherits_from_queue_abstract(self):
        self.assertTrue(issubclass(TestQueueAbstract.ConcreteQueue, QueueAbstract))

    def test_concrete_queue_has_abstract_methods_implemented(self):
        concrete_queue = TestQueueAbstract.ConcreteQueue(config=None)
        self.assertTrue(callable(concrete_queue.send))
        self.assertTrue(callable(concrete_queue.add))
        self.assertTrue(callable(concrete_queue.remove))
        self.assertTrue(callable(concrete_queue.get_items))


if __name__ == '__main__':
    unittest.main()
