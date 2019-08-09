import unittest
from service import ContractService


# python3 -m unittest test.test_contract_2_clusters
class TestContract(unittest.TestCase):

    def setUp(self):
        self.cs = ContractService(force_update=False)

    def test_invoke(self):
        self.cs.test_invoke()
