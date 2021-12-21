Setup Project
=============


Create project directory and venv 
---------------------------------

.. code-block:: bash

    $ mkdir -p ~/projects/MyNewProject
    $ python3.10 -m venv venv
    $ source venv/bin/activate


Install PAB and initialize project
----------------------------------

.. code-block:: bash

    (venv) $ pip install PyAutoBlockchain
    (venv) $ pab init  # Initialize project in current directory
