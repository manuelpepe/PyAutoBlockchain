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
* `envs.toml`: Environment variables set for each project.
* `conftest.py`: Pytest fixtures.


## Running tests

The recommended way to run integration tests is using [act](https://github.com/nektos/act).

With act you can run:

```
$ act -j integration-tests
```

to run integration from the github actions tests inside a docker container.

The other way is to use local installations of (truffle)[https://github.com/trufflesuite/truffle] and ganache [ganache](https://github.com/trufflesuite/ganache) and just run:

```
$ ./integration-tests.sh
```


## Parts

### Solidity Smart Contracts

To fully test integrations, solidity smart contracts are built and deployed
from the `contracts/` directory.

[Truffle Suite](https://trufflesuite.com/) is used to aid in the development, testing and 
deployment of the Smart Contracts.

#### Local Setup

Install truffle and ganache-cli.

#### Building, testing and deploying contracts to the local network

Run ganache-cli on a separate terminal to start the local network.
Then, from the `contracts/` directory:

* `truffle test` to run tests
* `truffle migrate` to deploy using migration scripts


### PAB Projects

Integration tests run PAB projects against a local development blockchain.
Multiple testing projects can be found in the `projects/` directory, and new
ones can be added.

#### Contracts

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

### Tests

PAB provides a `setup_project(project_name)` fixture that automatically sets up 
the corresponding project (from `projects/{project_name}`).

The setup includes:

* Copying the project files to a temp directory
* Changing the CWD to the new temp directory
* Setting the basic config values for testing ( # TODO )
    * blockchain: Ganache
    * chainId: 1337
    * endpoint: `http://127.0.0.1:8545/`
    * accounts from ganache
* Setting all environments variables related to the given project, as defined in the `envs.toml` file.
* Replacing the contract addresses in `contracts.json` with the matching addresses in the development network.
