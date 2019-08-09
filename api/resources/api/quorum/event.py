from flask import jsonify
from flask_restful import Resource

from config import api, quorum_contract_resource_logger
from service import EventService, util


class WriteLog(Resource):
    @staticmethod
    def post():
        try:
            data = util.get_request_json()
            print(data)
            log = data["log"]
            if not log:
                quorum_contract_resource_logger.warning('"log" not sent in request.')
                return jsonify({'message': '"log" not sent in request.', 'status': '0'})

        except Exception as err:
            quorum_contract_resource_logger.exception(str(err))
            return jsonify({'message': 'Could not read params in request.', 'status': '0'})

        try:
            r, tx_hash, result = EventService().write_event(log)
            if not r:
                return jsonify({'message': 'Could not write log.', 'status': '0'})

            r, index = EventService().get_index()
            if not r:
                return jsonify({'message': 'Could not get index.', 'status': '0'})

            status = '1' if r else '0'
            resp = {
                'message': 'success',
                'status': status,
                'index': index,
                'tx_hash': tx_hash,
                'block_number': result
            }

            return jsonify(resp)

        except Exception as err:
            quorum_contract_resource_logger.exception(str(err))
            return jsonify({'message': 'Error while writing log.', 'status': '0'})


class ReadLog(Resource):
    @staticmethod
    def post():
        try:
            data = util.get_request_json()

            start_index = 0
            end_index = 0
            if 'start_index' in data:
                start_index = int(data['start_index'])
            if 'end_index' in data:
                end_index = int(data['end_index'])

        except Exception as err:
            quorum_contract_resource_logger.exception(str(err))
            return jsonify({'message': 'Could not read params in request.', 'status': '0'})

        try:
            logs = EventService().get_events(start_index, end_index)
            resp = {
                'message': 'success',
                'status': '1',
                'logs': logs
            }

            return jsonify(resp)

        except Exception as err:
            quorum_contract_resource_logger.exception(str(err))
            return jsonify({'message': 'Could not read logs.', 'status': '0'})


def __register_event_resources():
    api.add_resource(WriteLog, '/blocktest/api/log/write')
    api.add_resource(ReadLog, '/blocktest/api/log/read')
