const {BN, balance, ether, should, shouldFail, time} = require('openzeppelin-test-helpers');

Object.assign(Object.prototype, {
    array(x) {
        return Object.values(this);
    }
});

contract('EventLog', ([deployer, account1]) => {

    before(async () => {
        this.pk = [""];
    });

    beforeEach(async () => {
        //console.log(`****************** before *********************`);
    });

    afterEach(async () => {
        console.log("***************************************");
    });

    it('Deploy EventLog', async () => {
        console.log(`deployer : ${deployer}`);

        await web3.eth.personal.unlockAccount(deployer, "", 360000);
        //await web3.eth.personal.unlockAccount(account1, "", 360000);

        const load_contract = async(name, addr)=>{
            return await artifacts.require(`./contracts/${name}.sol`).at(addr);
        }

        const deploy_contract = async(name)=>{
            return await artifacts.require(`${name}`).new({from: deployer}); // privateFor:[this.pk[1], this.pk[2]]
        }

        const contract_name = "EventLog";
        this[contract_name] = await deploy_contract(contract_name);
        console.log(`"EventLog": "${this[contract_name].address}"`);
    });

});
