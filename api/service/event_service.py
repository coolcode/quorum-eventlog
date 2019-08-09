from config import quorum_api_service_logger
from config.quorum.config_quorum import network, abi, instances
from .api_service import ApiService
from .util import util


class EventService(ApiService):

    def __init__(self):
        try:
            ApiService.__init__(self)
            self.event_log_address = instances["EventLog"]
            self.event_log_abi = abi["EventLog"]["abi"]
        except Exception as ex:
            quorum_api_service_logger.exception(str(ex))

    def write_event(self, msg):
        r, tx_hash, block_number, op = self.invoke(self.event_log_address, self.event_log_abi, "write", [msg], None, None)
        print("block number: " + str(block_number))
        return r, tx_hash, block_number

    def get_index(self):
        r, tx_hash, index, op = self.invoke(self.event_log_address, self.event_log_abi, "index", [], None, None)
        return r, index
            
    def get_events(self, start_index=0, end_index=0, account=None, gas=None, node_index=0):
        self.use_web3(node_index)

        if account is None:
            account = self.web3.eth.accounts[0]

        self.unlock_account(account)
        if not gas:
            gas = self.gas

        if not end_index:
            end_index = start_index + 10 - 1
        if end_index < start_index:
            raise ValueError("'end_index' cannot be less than 'start_index'")

        if not start_index and not end_index:
            filters = {}
        else:
            filters = {'index': range(start_index, end_index+1)}

        contract = self.web3.eth.contract(address=self.event_log_address, abi= self.event_log_abi)
        event_filter = contract.events.Log.createFilter(fromBlock=0, toBlock="latest", argument_filters=filters)
        logs = event_filter.get_all_entries()
        # quorum_api_service_logger.info("logs: " + str(logs))
        msgs = []
        for x in logs:
            log = x.args
            msgs.append({"index": log['index'],
                         "content": log['content'],
                         "date": log['date'],
                         "date_str": util.tick_to_date(log['date'])})
        return msgs
