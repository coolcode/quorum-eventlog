import unittest
from config.quorum.config_quorum import network, abi
from service import ApiService, BlockService


# python3 -m unittest test.test_contract or python3 -m unittest test/test_contract.py
class TestContract(unittest.TestCase):
    compiled_json = abi["EventLog"]
    deployer = BlockService.str2address("0x80d317d4A583F2bB63448ECf81DF5aee1aA7AB4c")
    invoker = BlockService.str2address("0x80d317d4A583F2bB63448ECf81DF5aee1aA7AB4c")
    contract_address = "0x49b8493Ccca0134befB8289CCE7fD047a6a1A355"

    def test_deploy(self):
        api = ApiService()
        r, tx_hash, contract_address = api.deploy(self.compiled_json["bytecode"], self.compiled_json["abi"], self.deployer, None, None, None)
        print("contract_address: " + str(contract_address))
        self.assertIsNotNone(contract_address)
        return contract_address

    def test_invoke(self):
        api = ApiService()
        print("invoke contract: " + self.contract_address)
        for i in range(10):
            r, tx_hash, block_number, op = api.invoke(self.contract_address, self.compiled_json["abi"], "write", ["Hello World "+ str(i)], self.invoker, None, [])
            print("block number: " + str(block_number))

            self.assertIsNotNone(block_number)

        # r, tx_hash, invoke_result, op = api.invoke(self.contract_address, self.compiled_json["abi"], "get", [], self.invoker, None, [])
        # print("invoke result: " + str(invoke_result))
        #
        # self.assertIsNotNone(invoke_result)
