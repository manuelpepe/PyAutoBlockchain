# Integration Testing Manual

Integration Testing involves testing PAB Tasks agains live contracts deployed on 
local ganache blockchain.

This document provides an overview of the Integration Testing system and it's parts.


## Objective

Integration tests aim to assure developers and users that the system (PAB) works
correctly when interacting with real systems.

Interacting with systems can mean:

* Blockchain querys and transactions
* SMTP email delivery
* RabbitMQ message delivery


## Structure

* `contracts/`: Source code for solidity contracts. Truffle project structure.
* `projects/`: PAB Projects.
* `tests/`: Pytest integration tests.
* `.secrets.example.toml`: Example `.secrets.toml` file. (See [Secrets](#secrets))
* `conftest.py`: Pytest fixtures.


## Solidity Smart Contracts

To fully test integrations, solidity smart contracts are built and deployed
from the `contracts/` directory.

[Truffle Suite](https://trufflesuite.com/) is used to aid in the development, testing and 
deployment of the Smart Contracts.

### Local Setup

Install truffle and ganache-cli.

### Building, testing and deploying contracts to the local network

Run ganache-cli on a separate terminal to start the local network.
Then, from the `contracts/` directory:

* `truffle test` to run tests
* `truffle migrate` to deploy using migration scripts


## PAB Projects

Integration tests run PAB projects against a local development blockchain.
Multiple testing projects can be found in the `projects/` directory, and new
ones can be added.

### Contracts

Contract addresses may change between test runs, as they are redeployed every time the integration
tests run. The way to always point to the correct contract is by using the `{ContractName}` syntax in the 
PAB Project's `contracts.json` as the contract address.

For example, if you are deploying and using a contract name `TokenController`, the following `contracts.json` will
populate to the correct address when the tests run:

```json
{
    "TokenController": {
        "address": "{TokenController}",
        "abifile": "TokenController.abi"
    }
}
```

### Secrets

Some sensitive data is needed to run PAB projects. Namely, a (sometimes private) RPC,
your private key, your public address, SMTP details, etc.

To avoid setting these values inside the each testing project, and making them 
publicly available, Environment Variables are loaded from a `.secrets.toml` file.

This file is populated by the CI when running in a pipeline, or can be manually populated
if you wish to run outside of CI.

For an usage example, see `secrets.example.toml`.


## Tests

PAB provides a `setup_project(project_name)` fixture that automatically sets up 
the corresponding project (from `projects/{project_name}`).

The setup includes:

* Copying the project files to a temp directory
* Changing the CWD to the new temp directory
* Setting the basic config values for testing ( # TODO )
    * blockchain: Ganache
    * chainId: 1337
    * endpoint: `http://127.0.0.1:8545/`
    * myAddress: *address 0 on ganache*
    * Private Key: *private key for address 0 on ganache*
* Setting all environments variables related to the given project, as defined in the `.secrets.toml` file.
* Replacing the contract addresses in `contracts.json` from the current addresses in the development network.


Once setup, you can use the helper methods in `pab.test` to run tasks on-demand and make assertions agains the contracts
state or anything else (files, services, values).

For example, you can run a task that will set a value, and then assert that the value was setted.
