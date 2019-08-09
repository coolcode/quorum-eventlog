from flask import jsonify
from flask_restful import Resource

from config import api, quorum_contract_resource_logger
from config.quorum.config_quorum import instances
from service import ContractService, util


class InvokeContract(Resource):
    @staticmethod
    def post():
        try:
            data = util.get_request_json()

            c_name = data['contract']
            if not c_name:
                quorum_contract_resource_logger.warning('contract not sent in request.')
                return jsonify({'message': 'Contract not sent in request.', 'status': '0'})

            f_name = data['function']
            if not f_name:
                quorum_contract_resource_logger.warning('function not sent in request.')
                return jsonify({'message': 'Function not sent in request.', 'status': '0'})

            # optional params
            account = data['account'] if 'account' in data else None

            inputs = data['inputs'] if 'inputs' in data else []

            private_for = data['private_for'] if 'private_for' in data else []
        except Exception as err:
            quorum_contract_resource_logger.exception(str(err))
            return jsonify({'message': 'Could not read params in request.', 'status': '0'})

        try:
            r, tx_hash, result, op = InvokeContract.invoke(c_name, f_name, inputs, account, private_for)

            status = '1' if r else '0'
            if op == 'call':
                return jsonify({
                    'message': 'success',
                    'status': status,
                    'result': result,
                    'op': op
                })
            else:
                resp = {
                    'message': 'success',
                    'status': status,
                    'tx_hash': tx_hash,
                    'block_number': result,
                    'op': op
                }

                return jsonify(resp)

        except Exception as err:
            quorum_contract_resource_logger.exception(str(err))
            return jsonify({'message': 'Could not invoke contract.', 'status': '0'})

    @staticmethod
    def invoke(name, func, inputs=None, account=None, private_for=[]):
        contracts = instances
        if contracts is {} or not contracts:
            quorum_contract_resource_logger.warning('Contracts not deployed yet!!')
            return False, None, 'Contracts not deployed!', 'Err'

        quorum_contract_resource_logger.info("Invoking: [%s] (%s, %s) ..." % (func, name, contracts[name]))

        r, tx_hash, invoke_result, op = ContractService().invoke(name, func, inputs, account, private_for)

        return r, tx_hash, invoke_result, op


def __register_contract_resources():
    api.add_resource(InvokeContract, '/blocktest/api/quorum/invoke')
