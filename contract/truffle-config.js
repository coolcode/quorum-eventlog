
module.exports = {
  /**
   * Networks define how you connect to your ethereum client and let you set the
   * defaults web3 uses to send transactions. If you don't specify one truffle
   * will spin up a development blockchain for you on port 9545 when you
   * run `develop` or `test`. You can ask a truffle command to use a specific
   * network from the command line, e.g
   *
   * $ truffle test --network <network-name>
   */

  networks: {
        development: {
            host: "127.0.0.1",
            port: 7545,
            network_id: "*"
        },
        quorum1: {
            host: "54.198.73.127",
            port: 22001,
            network_id: "*",
            gasPrice: 0,
            gas: 4500000,
            type: "quorum"
        },
  },

  // Set default mocha options here, use special reporters etc.
  mocha: {
    //timeout: 10000000
    timeout: false
  },

  // Configure your compilers
  compilers: {
    solc: {
      // version: "0.5.1",    // Fetch exact version from solc-bin (default: truffle's version)
      // docker: true,        // Use "0.5.1" you've installed locally with docker (default: false)
      // settings: {          // See the solidity docs for advice about optimization and evmVersion
      //  optimizer: {
      //    enabled: false,
      //    runs: 200
      //  },
      //  evmVersion: "byzantium"
      // }
    }
  }
}
