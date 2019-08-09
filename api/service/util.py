from datetime import datetime, timedelta
from flask import request
import os
import json


class util:
    @staticmethod
    def uid():
        return datetime.now().strftime('%Y%m%d%H%M%S%f')

    @staticmethod
    def write_json(filename, o):
        base_dir = "files/"

        if not os.path.exists(base_dir):
            if os.path.exists("../files/"):
                base_dir = "../files/"
            else:
                os.makedirs(base_dir)
        with open(base_dir + filename, 'w') as file:
            file.write(json.dumps(o))

    @staticmethod
    def read_json(filename):
        base_dir = "files/"
        try:
            with open(base_dir + filename, 'r') as file:
                return json.loads(file.read())
        except:
            base_dir = "../files/"
            try:
                with open(base_dir + filename, 'r') as file:
                    return json.loads(file.read())
            except:
                return {}

    @staticmethod
    def get_request_json():
        json_obj = {}

        if request.method == 'POST':
            try:
                json_obj = request.get_json(force=True)
                return json_obj
            except:
                pass

            try:
                # load into json if received a string
                if isinstance(json_obj, str):
                    return json.loads(json_obj)
            except Exception as ex:
                print('get_request_json. Object could not be parsed. ' + str(ex))
                return {'message': 'Unable to read the sent object.', 'status': '0'}

    @staticmethod
    def tick_to_date(ticks):
        _date = datetime.fromtimestamp(ticks // 1000000000)
        return _date.strftime("%Y-%m-%dT%H:%M:%S") + ".{}Z".format((ticks % 100000000) // 100000)
