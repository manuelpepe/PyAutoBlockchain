## 0.4 (ON-DEV)

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