from flask import jsonify
from flask_restful import Resource

from config import api, quorum_account_resource_logger
from service import util, ContractService


class InitAccounts(Resource):
    @staticmethod
    def post():
        try:
            cs = ContractService()
        except Exception as ex:
            quorum_account_resource_logger.exception(str(ex))
            return jsonify({'message': 'Could not initialize account(s).', 'status': '0'})

        try:
            data = util.get_request_json()

            force_update_account = True if ('update_account' in data and data['update_account'] == 'True') else False
            force_update_contract = True if ('update_contract' in data and data['update_contract'] == 'True') else False
        except:
            # setting default as False in case of any exceptions
            force_update_account = False
            force_update_contract = False

        try:
            quorum_account_resource_logger.info('force_update_account = ' + str(force_update_account))
            quorum_account_resource_logger.info('force_update_contract = ' + str(force_update_contract))
            if not force_update_account:
                accounts = util.read_json(get_account_file_path())
                if len(accounts) > 0:
                    quorum_account_resource_logger.info('Accounts already exist. Successfully returned.')
                    return jsonify({
                        'message': 'success',
                        'status': '1',
                        'accounts': accounts
                    })
        except Exception as ex:
            quorum_account_resource_logger.exception(str(ex))

        try:
            cs.setup_accounts(force_update_account)

            # only deploy contract if explicitly asked
            if force_update_contract:
                cs.setup_contracts(force_update_contract)
        except Exception as err:
            quorum_account_resource_logger.exception(str(err))
            return jsonify({'message': 'Could not create account(s).', 'status': '0'})

        try:
            # read accounts
            accounts = util.read_json(get_account_file_path())

            if len(accounts) > 0:
                quorum_account_resource_logger.info('Successfully initialized accounts')
                return jsonify({
                    'message': 'Successfully initialized account(s).',
                    'status': '1',
                    'accounts': accounts
                })
            else:
                quorum_account_resource_logger.warning('Could not initialize the accounts.')
                return jsonify({'message': 'Could not initialize accounts!.', 'status': '0'})
        except Exception as ex:
            quorum_account_resource_logger.exception(str(ex))
            return jsonify({'message': 'Something went wrong.', 'status': '0'})


class GetAccounts(Resource):
    @staticmethod
    def get():
        try:
            cs = ContractService()
            cluster_1_node_index = cs.cluster_1_node_index
            cluster_2_node_index = cs.cluster_2_node_index
        except Exception as ex:
            quorum_account_resource_logger.exception(str(ex))
            return jsonify({'message': 'Could not get account(s).', 'status': '0'})

        try:
            accounts = util.read_json(get_account_file_path())
            quorum_account_resource_logger.info('GetAccounts successful')
            return jsonify({
                'message': 'success',
                'status': '1',
                'accounts': accounts
            })
        except Exception as ex:
            quorum_account_resource_logger.exception(str(ex))
            return jsonify({'message': 'Something went wrong.', 'status': '0'})


def get_account_file_path():
    return "accounts_%s.json" % "uid"


def __register_account_resources():
    api.add_resource(InitAccounts, '/blocktest/api/quorum/init_accounts')
    api.add_resource(GetAccounts, '/blocktest/api/quorum/get_accounts')
