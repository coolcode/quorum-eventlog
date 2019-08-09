from flask import Flask
from flask_cors import CORS
application = Flask(__name__)
CORS(application)

# application.config.from_object('config.config_deploy')
# application.config.from_object('config.config_default')  # this is for local testing
application.config.from_object('config.config_dev')
# application.config.from_object('config.config_online_test')  # this is for online-testing environment

"""
Create the global resource registration
"""
from flask_restful import Api
api = Api(application)

"""
Initialize the global logging system
"""
import logging
# set up logging to file - see previous section for more details
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename='access_log.log',
                    filemode='w')
# define a Handler which writes INFO messages or higher to the sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.INFO)
# set a format which is simpler for console use
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
# tell the handler to use this format
console.setFormatter(formatter)
# add the handler to the root logger
logging.getLogger('').addHandler(console)

"""
Initalize the loggers for each resource
"""
gateway_manager_logger = logging.getLogger('gateway.gateway_manager')
authorization_logger = logging.getLogger('authorize.authorize')
db_service_logger = logging.getLogger('service.db_service')
quorum_api_service_logger = logging.getLogger('service.api_service')
quorum_block_service_logger = logging.getLogger('service.block_service')
util_logger = logging.getLogger('service.util')
quorum_get_block_number_resource_logger = logging.getLogger('resources.api.block.get_block_number')
quorum_account_resource_logger = logging.getLogger('resources.api.quorum.account')
quorum_contract_resource_logger = logging.getLogger('resources.api.quorum.contract')


# initialize resources
def __init_resource():
    from resources.api.quorum.account import __register_account_resources
    from resources.api.quorum.contract import __register_contract_resources
    from resources.api.quorum.event import __register_event_resources

    # __register_get_block_number_resource()
    __register_account_resources()
    __register_contract_resources()
    __register_event_resources()


# __init_resource()
