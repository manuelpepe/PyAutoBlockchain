## 0.5 (***WIP***)

* New `init` command.
* New optional `PyAutoBlockchain[ui]` extension to install [PABUI](https://github.com/manuelpepe/PABUI).
* New config loading from ENVVARS/.env file for sensitive data (Personal 0xAddress, RPC, SMTP). 
* Removed `edit-config` command.
* Removed deprecated functions from `pab.utils`.
* Multiple accounts.
* Load accounts from ENVVARS named `PAB_PK<index>`. `index` will be the index in `BaseStrategy.accounts`.
* Strategy API Change: Changed `BaseStrategy._transact(func, args)` to `BaseStrategy.transact(acc, func, args)`. First parameter should be an Account from `BaseStrategy.accounts`.
* Strategy API Change: Removed `BaseStrategy.blockchain.read_contract`, now use `BaseStrategy.contracts.get`
* Strategy API Change: New property `BaseStrategy.contracts`. 
* Strategy API Change: New property `BaseStrategy.accounts`. 

## 0.4 (2021-11-11)

* Fix `edit-config` command.
* Removed eager config loading.
* New `-j/--json` parameter in `list-strategies` to export strategy data in JSON format for PABUI or other tools. 

## 0.3.4 (2021-11-04)

* Usage without private keys, if you are going to use read-only abis.

## 0.3.3 (2021-06-22)

* Removed MANIFEST.in in favor of `package_data`

## 0.3.2 (2021-06-22)

* Correctly fix defaults config file

## 0.3.1 (2021-06-22)

* Fix exception "config.defaults.json not found" (renamed to config.sample.json)

## 0.3 (2021-06-20)

Transaction gas customization improved. New option to estimate gas usage for transaction.

* TransactionHandler raises TransactionError if the receipt status != 1
* TransactionHandler may estimate transaction gas usage (if enabled)
* New configs for transaction gas (enable estimation, gasPrice configuration)
* Renamed config `transactionTimeout` to `transactions.timeout` (see pab/resources/config.defaults.json for full schema with default values)

## 0.2.2 (2021-06-15)

Initial Release