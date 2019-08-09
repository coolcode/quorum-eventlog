import unittest
from service import EventService


# python3 -m unittest test.test_read_event_log
class TestContract(unittest.TestCase):
    contract_address = "0x49b8493Ccca0134befB8289CCE7fD047a6a1A355"

    def test_read(self):
        es = EventService()
        logs = es.get_events(self.contract_address, 2, 13)
        print("logs: " + str(logs))
        self.assertIsNotNone(logs)

