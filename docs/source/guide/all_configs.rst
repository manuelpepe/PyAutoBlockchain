.. _All Configs:

All Configs
+++++++++++


.. exec::

    from pathlib import Path
    from pab.config import SCHEMA
    from projectutils.config import generate_docs
    SOURCE_DIR = Path(__file__).parent.absolute()
    print(generate_docs(SCHEMA))
