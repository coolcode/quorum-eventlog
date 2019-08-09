from datetime import datetime

from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware
from config import quorum_block_service_logger
from config.quorum.config_quorum import network, abi, public_keys, nodes
import time


class BlockService:
    def __init__(self, node_index=0):
        try:
            self.publicKeys = public_keys
            self.web3_nodes = []
            for node in nodes:
                web3_node = Web3(HTTPProvider(node))
                web3_node.middleware_stack.inject(geth_poa_middleware, layer=0)
                self.web3_nodes.append(web3_node)

            self.web3 = None
            self.use_web3(node_index)
            self.contracts = {}
            # self.load_contracts()

        except Exception as ex:
            quorum_block_service_logger.exception(str(ex))

    def use_web3(self, node_index):
        if isinstance(node_index, int):
            self.web3 = self.web3_nodes[node_index]
        elif str(node_index).startswith('http'):
            self.web3 = Web3(HTTPProvider(node_index))
        else:
            quorum_block_service_logger.exception("unsupported type: '%s', value: %s" % (str(type(node_index)), str(node_index)))
            return

    def load_contracts(self):
        try:
            for contractName in abi:
                self.contracts[contractName] = self.web3.eth.contract(address=network["contracts"][contractName], abi=abi[contractName])  # , {"gas":800000}
                setattr(self, contractName, DynamicContract(self.web3, self.contracts[contractName]))
        except Exception as ex:
            quorum_block_service_logger.exception(str(ex))

    def create_account(self):
        try:
            return self.web3.personal.newAccount('')
        except Exception as ex:
            quorum_block_service_logger.exception(str(ex))
            return None

    def unlock_account(self, account):
        try:
            return self.web3.personal.unlockAccount(account, '', duration=864000000)
        except Exception as ex:
            quorum_block_service_logger.exception("unlock_account error:" + str(ex))
            return None

    @staticmethod
    def get_default_accounts():
        try:
            return network["accounts"]
        except Exception as ex:
            quorum_block_service_logger.exception(str(ex))
            return None

    def get_contract(self, name, address):
        try:
            return DynamicContract(self.web3, self.web3.eth.contract(address=address, abi=abi[name]))
        except Exception as ex:
            quorum_block_service_logger.exception(str(ex))
            return None

    def wei2eth(self, v):
        try:
            return self.web3.fromWei(v, 'ether')
        except Exception as ex:
            quorum_block_service_logger.exception(str(ex))
            return None

    def eth2wei(self, v):
        try:
            return self.web3.toWei(v, 'ether')
        except Exception as ex:
            quorum_block_service_logger.exception(str(ex))
            return None

    @staticmethod
    def str2address(v):
        try:
            return Web3.toChecksumAddress(v)
        except Exception as ex:
            quorum_block_service_logger.exception(str(ex))
            return None

    @staticmethod
    def long2date(v):
        try:
            return datetime.fromtimestamp(float(v) / 1000000000).strftime('%m/%d/%Y %H:%M:%S')
        except Exception as ex:
            quorum_block_service_logger.exception(str(ex))
            return None

    def wait_confirm(self, tx_hash):
        max_retries = 60
        i = 0
        while i < max_retries:
            tx_receipt = self.web3.eth.getTransactionReceipt(tx_hash)
            if tx_receipt:
                quorum_block_service_logger.info('tx_receipt = ' + str(tx_receipt))
                return True
            else:
                time.sleep(1)
                # try again
            i += 1
        quorum_block_service_logger.warning('Could not get tx receipt after 10 tried!')
        return False

    def get_block(self, block_number):
        return self.web3.eth.getBlock(block_number)


class DynamicContract:
    def __init__(self, web3, contract):
        try:
            self.web3 = web3
            self.contract = contract
            self.address = contract.address
            functions = contract.functions
            for funName in functions:
                setattr(self, str(funName), functions[funName])
                # quorum_block_service_logger.info('function: ' + str(funName))

            self.events = contract.events
            events = contract.events
            for event in events._events:
                event_name = event['name']
                # quorum_block_service_logger.info('event:' + event_name)
                setattr(self, event_name, self.dynamic_event(events[event_name]))
        except Exception as ex:
            quorum_block_service_logger.exception(str(ex))

    def dynamic_event(self, event):
        def get_event_data(tx_hash):
            try:
                tx_receipt = self.web3.eth.getTransactionReceipt(tx_hash)
                if not tx_receipt:
                    quorum_block_service_logger.warning('tx_receipt is "' + str(type(tx_receipt)) + '"')
                    return None

                logs = event().processReceipt(tx_receipt)
                if len(logs) == 0:
                    quorum_block_service_logger.warning('No logs found for tx # ' + str(tx_hash) + ' receipt ' + str(tx_receipt))
                    return None
                else:
                    return logs[0].args
            except Exception as ex:
                quorum_block_service_logger.exception(str(ex))
                return None

        return get_event_data
