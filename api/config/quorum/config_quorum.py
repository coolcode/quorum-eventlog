import json, os

config_json = {
    "env": "quorum",
    "networks": {
        "quorum": {
            "accounts": [
            ],
            "nodes": [
                "http://54.198.73.127:22001",
                "http://54.198.73.127:22002",
                "http://54.198.73.127:22003",
                "http://54.198.73.127:22004",
                "http://54.198.73.127:22005",
            ],
            "public_keys": [
                ["SWsCtVlQxa74j3ZJitbx5Vv0KSGaYvlv5byih8zcSFI=",
                 "A8+jJ/1SLfzz/CwH7lrCv9St/kjYcbbMgMEc9VdecWc=",
                 "+9ym/vApc5ozXs7USGCJvhbZLeVz/0uDEToqtkRIXHM=",
                 "2V9HFgCvgnZeVd3JBNYXcS7j5bIEPuiFWM9GVQpQGWw=",
                 "fIx89UjOkpYnbXztMCA5ewBiqCZZeU5iKoe5KXL+SUo="]
            ],
            "contracts": [
                "EventLog"
            ],
            "instances": {
                "EventLog": "0x42959Ff6DD4CB6fCab65dc0d65e1BBFADf0D50C8"
            }
        }
    }
}

root_path = os.path.dirname(os.path.abspath(__file__))


def load_abi(name):
    file_path = root_path + "/abi/%s.json" % name
    with open(file_path) as f:
        info_json = json.load(f)
        return info_json
    # return ""


network = config_json["networks"][config_json["env"]]

abi = {}
instances = {}
if "contracts" in network:
    for contractName in network["contracts"]:
        abi[contractName] = load_abi(contractName)
        instances[contractName] = network["instances"][contractName]

public_keys = []
if "public_keys" in network:
    public_keys = network["public_keys"]

nodes = []
if "nodes" in network:
    nodes = network["nodes"]
