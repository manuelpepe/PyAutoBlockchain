Setup Project
=============


Create project directory and venv
---------------------------------

First you need to create a directory to contain your project files
and create a virtualenv.

.. code-block:: bash

    $ mkdir -p ~/projects/MyNewProject
    $ python3.10 -m venv venv
    $ source venv/bin/activate


Install PAB and initialize project
----------------------------------

Then install the `PyAutoBlockchain` dependency in your virtualenv
and run `pab init` to create the basic project structure.

.. code-block:: bash

    (venv) $ pip install PyAutoBlockchain
    (venv) $ pab init  # Initialize project in current directory


Project Structure
-----------------


...
