from config.quorum.config_quorum import network, abi
from service import ApiService, BlockService
from .util import util


class ContractService:
    api = ApiService()

    accounts = []

    contracts = {}

    def __init__(self, force_update=False):
        self.setup_accounts(force_update)
        self.setup_contracts(force_update)

    def setup_accounts(self, force_update=False):
        # checking the accounts
        self.accounts = util.read_json('accounts_uid.json')

        if self.accounts == {} or len(self.accounts) == 0 or force_update:
            print('-> No accounts present. Creating now ..')
            self.accounts = []
            for i in range(5):
                self.api.use_web3(i)
                account = self.api.create_account()

                if account is None:
                    print('-> Error: ContractService setup No.[%s] account returned none.' % str(i + 1))
                    return False
                else:
                    print('-> Created account %s: %s' % (str(i + 1), account))
                self.accounts.append(account)

            # save accounts
            util.write_json('accounts_uid.json', self.accounts)
            print('-> Successfully created and saved ' + str(len(self.accounts)) + ' accounts.')

        print('-> ' + str(len(self.accounts)) + ' accounts present in files/accounts_uid.json')

        self.deployer = BlockService.str2address(self.accounts[0])
        print('--> Initialized accounts.')

    def setup_contracts(self, force_update=False):
        # checking if contracts have been deployed before
        self.contracts = util.read_json('deployed_contract_address.json')
        if self.contracts != {}:
            print('--> Project was initialized previously!')
            if not force_update:
                print('----> Please force_update again by changing the flag if required..')
                return

        print('----> Force deploying and initializing contracts ..')

        # deploying contracts
        print('--> Deploying contracts..')
        self.deploy("EventLog")

        util.write_json('deployed_contract_address.json', {})
        util.write_json('deployed_contract_address.json', self.contracts)
        print('--> Saved deployed contract details to files/deployed_contract_address.json')

    def deploy(self, name, inputs=None, account=None, privateFor=[], alias=None, node_index=0):
        if account is None:
            account = self.deployer

        r, tx_hash, contract_address = self.api.deploy(abi[name]["bytecode"], abi[name]["abi"], account, None, inputs, privateFor, node_index)
        self.contracts[name] = {"contract_address": contract_address, "abi": abi[name]["abi"]}

        if alias is not None:
            self.contracts[alias] = {"contract_address": contract_address, "abi": abi[name]["abi"]}
            print("contract_address [" + alias + "]: " + str(contract_address))
        else:
            print("contract_address [" + name + "]: " + str(contract_address))

        return contract_address, abi[name]["abi"]

    def invoke(self, name, func, inputs=None, account=None, privateFor=[], node_index=0):
        if account is None:
            account = self.deployer

        print("[node=%s] Invoking [%s] (%s, %s) ..." % (str(node_index), func, name, self.contracts[name]["contract_address"]))

        r, tx_hash, invoke_result, op = self.api.invoke(self.contracts[name]["contract_address"], self.contracts[name]["abi"], func, inputs, account, None, privateFor, node_index)
        if op == "transact":
            print(" --> %s [%s][op=%s]: %s (block number)" % (name, func, op, str(invoke_result)))
        else:
            print(" --> %s [%s][op=%s]: %s" % (name, func, op, str(invoke_result)))

        return r, tx_hash, invoke_result, op

    def test_invoke(self):
        self.invoke("EventLog", "write", ["Hello World!"])

    def test_invoke_2(self):
        i = 0
        while(i<100):
            self.invoke("EventLog", "write", ["Hello World " + str(i)])
            i+=1
        print("Done!")
