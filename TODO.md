## Remove deprecated functions from pab.utils

## Give more descriptive error when unexpected parameters are passed to tasks. E.g. traceback:
```
Traceback (most recent call last):
  File "/mnt/d/Dev/ACSInfoGath/venv/bin/pab", line 33, in <module>
    sys.exit(load_entry_point('PyAutoBlockchain', 'console_scripts', 'pab')())
  File "/mnt/d/Dev/PyAutoBlockchain/pab/cli.py", line 136, in main
    args.func(args, logger)
  File "/mnt/d/Dev/PyAutoBlockchain/pab/cli.py", line 82, in run
    queue = QueueLoader(blockchain).load()
  File "/mnt/d/Dev/PyAutoBlockchain/pab/queue.py", line 118, in load
    return self._create_queue_from_list(tasks)
  File "/mnt/d/Dev/PyAutoBlockchain/pab/queue.py", line 129, in _create_queue_from_list
    strat = self._create_strat_from_data(data)
  File "/mnt/d/Dev/PyAutoBlockchain/pab/queue.py", line 137, in _create_strat_from_data
    return strat_class(self.blockchain, data["name"], **data.get("params", {}))
TypeError: __init__() got an unexpected keyword argument 'contract'
```
