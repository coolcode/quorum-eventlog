import time

from config import quorum_api_service_logger
from .block_service import BlockService


# from solcx import install_solc, get_solc_version_string, set_solc_version
# from .compile_service import compile_files, compile_standard
# from .util import util
# import requests


class ApiService(BlockService):
    def __init__(self):
        try:
            BlockService.__init__(self)
            self.gas = 204800000
            # install_solc('v0.4.25', allow_osx=True)
            # install_solc('v0.5.9', allow_osx=True)
            # set_solc_version('v0.4.25')
        except Exception as ex:
            quorum_api_service_logger.exception(str(ex))

    def deploy(self, bytecode, abi, account, gas, inputs, privateFor = None, node_index=0):
        if privateFor is None:
            privateFor = []
        if privateFor is not None and node_index in privateFor:
            privateFor.remove(node_index)

        self.use_web3(node_index)
        self.unlock_account(account)
        if not bytecode.startswith('0x'):
            bytecode = '0x' + bytecode
        if not gas:
            gas = self.gas
        contract = self.web3.eth.contract(abi=abi, bytecode=bytecode)
        if not inputs or len(inputs) == 0:
            param = {}
        else:
            param = self.get_constructor_param(abi, inputs)

        transaction_param = {'from': self.str2address(account), 'gas': gas}

        pk = self.get_public_keys(privateFor)

        if len(pk) > 0:
            # quorum_api_service_logger.info("privateFor: " + ', '.join(pk))
            transaction_param['privateFor'] = pk

        tx_hash = contract.constructor(**param).transact(transaction_param).hex()
        if self.wait_confirm(tx_hash):
            tx_receipt = self.web3.eth.getTransactionReceipt(tx_hash)
            return True, tx_hash, tx_receipt['contractAddress']
        else:
            return False, tx_hash, ''

    def invoke(self, contract_address, abi, function, inputs, account, gas, privateFor = None, node_index=0):
        if privateFor is None:
            privateFor = []
        if privateFor is not None and node_index in privateFor:
            privateFor.remove(node_index)

        pk = self.get_public_keys(privateFor)

        # Bruce: Don't use privateFor=[current node's key]!!! It only works in Tessera, not Constellation.
        # It's a bug in Constellation -> https://github.com/jpmorganchase/constellation/issues/47 https://github.com/jpmorganchase/quorum/issues/81
        # So, we use node_index to identify which quorum node it invokes and set privateFor=[]

        # if len(pk) > 0:
        #     if node_index is None:
        #         node_index = privateFor[0]

        self.use_web3(node_index)

        if account is None:
            account = self.web3.eth.accounts[0]

        # print("account: "+ str(account))
        self.unlock_account(account)
        if not gas:
            gas = self.gas

        contract = self.web3.eth.contract(address=contract_address, abi=abi)
        if inputs is None:
            inputs = []
        if not isinstance(inputs, list):
            inputs = [inputs]
        if not inputs or len(inputs) == 0:
            param = {}
        else:
            param = self.get_function_param(function, abi, inputs)

        op = ''
        for f in abi:
            if ('name' in f) and f['name'] == function:
                if ('stateMutability' in f) and (f['stateMutability'] == 'pure' or f['stateMutability'] == 'view' or f['stateMutability'] == 'constant'):
                    op = "call"
                else:
                    op = "transact"

        transaction_param = {'from': self.str2address(account), 'gas': gas}

        if len(pk) > 0:
            # quorum_api_service_logger.info("privateFor: " + ', '.join(pk))
            transaction_param['privateFor'] = pk
        elif node_index > 0:
            # quorum_api_service_logger.info("privateFor: []")
            transaction_param['privateFor'] = []

        if op == 'call':
            result = contract.functions[function](**param).call(transaction_param)
            return True, '', result, op
        else:
            tx_hash = contract.functions[function](**param).transact(transaction_param).hex()
            if self.wait_confirm(tx_hash):
                tx_receipt = self.web3.eth.getTransactionReceipt(tx_hash)
                return True, tx_hash, tx_receipt['blockNumber'], op
            else:
                return False, tx_hash, '', op

    def get_param(self, abi_inputs, argument_values):
        param = {}
        i = 0
        for input in abi_inputs:
            input_type = input['type']
            input_name = input['name']
            argument_value = argument_values[i]
            if input_type == "string":
                param[input_name] = argument_value
            elif input_type == "bool":
                param[input_name] = bool(argument_value)
            elif input_type.startswith("int") or input_type.startswith("uint"):
                param[input_name] = int(argument_value)
            elif input['type'] == "address":
                param[input_name] = self.str2address(argument_value)
            else:
                param[input_name] = argument_value
            i = i + 1

        return param

    def get_constructor_param(self, contract_abi, argument_values):
        for f in contract_abi:
            if ('type' in f) and ('inputs' in f) and (f['type'] == 'constructor'):
                abi_inputs = f["inputs"]
                if len(argument_values) != len(abi_inputs):
                    err = "The length of contract constructor should be " + str(len(abi_inputs))
                    raise ValueError(err)

                return self.get_param(abi_inputs, argument_values)

        return {}

    def get_function_param(self, function_name, contract_abi, argument_values):
        for f in contract_abi:
            if ('type' in f) and ('inputs' in f) and (f['type'] == 'function') and (f['name'] == function_name):
                inputs = f["inputs"]
                if len(argument_values) != len(inputs):
                    err = "The length of function '" + str(function_name) + "' should be " + str(len(inputs))
                    raise ValueError(err)

                return self.get_param(inputs, argument_values)

        return {}

    def get_public_keys(self, privateFor):
        pk = []
        for num in privateFor:
            n = int(num)
            if n > 0 and n < len(self.publicKeys):
                pk.append(self.publicKeys[n])
                # quorum_api_service_logger.info("private key " + str(n) + ": " + str(self.publicKeys[n]))
            else:
                quorum_api_service_logger.info("invalid index of private key: " + str(num))
        return pk

    def wait_confirm(self, tx_hash):
        max_retries = 10
        i = 0
        while i < max_retries:
            tx_receipt = self.web3.eth.getTransactionReceipt(tx_hash)
            if tx_receipt:
                # quorum_api_service_logger.info('tx_receipt = ' + str(tx_receipt))
                return True
            else:
                time.sleep(1)
                # try again
            i += 1
        quorum_api_service_logger.warning('Could not get tx receipt after 10 tried!')
        return False

    def get_block(self, block_number):
        return self.web3.eth.getBlock(block_number)

    # def compile(self, file_name, contract_name, path):
    #     # file_name = 'simplestorage.sol'
    #     # contract_name = 'simplestorage'
    #     contracts = compile_files([file_name], allow_paths=path)
    #
    #     # quorum_api_service_logger.info('contracts = ' + str(contracts))
    #     contract_interface = contracts[file_name + ":" + contract_name]  # [:-4]
    #     contract_bin = "0x" + contract_interface['bin']
    #     contract_abi = contract_interface['abi']
    #     return contract_bin, contrcontract_name, path):
    #     # file_name = 'simplestorage.sol'
    #     # contract_name = 'simplestorage'
    #     contracts = compile_files([file_name], allow_paths=path)
    #
    #     # quorum_api_service_logger.info('contracts = ' + str(contracts))
    #     contract_interface = contracts[file_name + ":" + contract_name]  # [:-4]
    #     contract_bin = "0x" + contract_interface['bin']
    #     contract_abi = contract_interface['abi']
    #     return contract_bin, contract_abi

    # def compile_s3(self, email, file_name, contract_name, user_code_records):
    #     # user_code_records = [{"root_dir": "test/77a2bfdde25ee12ce8853ccd4004f7eb511bddf5_KeyueWang-BT_1559154872399", "filename": "SimpleStorage.sol", "etag": "639d1d8efe5008b0811e67e5ec0ea34a"}]
    #     # read sol files from s3
    #     files = {}
    #     baseDir = '/tmp/sol/' + email + "/"
    #
    #     if not os.path.exists(baseDir):
    #         os.makedirs(baseDir)
    #     for record in user_code_records:
    #         key = '{}/{}'.format(record['root_dir'], record['filename'])
    #         code = util.get_s3_object_body(record['etag'], key)
    #         if code is not None:
    #             filename = str(record['filename'])
    #             files[filename] = code
    #             with open(baseDir + filename, 'w') as file:
    #                 file.write(code)
    #
    #     code_content = files[file_name]
    #
    #     if code_content.find('pragma solidity ^0.4') != -1 \
    #             or code_content.find('pragma solidity >=0.4') != -1 \
    #             or code_content.find('pragma solidity >0.4') != -1 \
    #             or code_content.find('pragma solidity 0.4') != -1:
    #         solc_version = 'v0.4.25'
    #     else:
    #         solc_version = 'v0.5.9'
    #     set_solc_version(solc_version)
    #     quorum_api_service_logger.info("Using solc version: " + solc_version)
    #     return self.compile(file_name, contract_name, baseDir)
