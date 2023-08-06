.. _dev-getting-started:

###############
Getting Started
###############

Before getting started, `fork this repo`_ and `clone your fork`_.

.. _fork this repo: https://help.github.com/en/github/getting-started-with-github/fork-a-repo
.. _clone your fork: https://help.github.com/en/github/creating-cloning-and-archiving-repositories/cloning-a-repository


***********************
Development Environment
***********************

This project uses ``pipenv`` to create Python virtual environment. This must be installed on your system before setting up your dev environment.

With pipenv installed, run ``make sync_all`` to setup your development environment. This will create all the requred virtual environments to work on runway, build docs locally, and run integration tests locally. The virtual environments all have Runway installed as editable meaning as you make changes to the code of your local clone, it will be reflected in all the virtual environments.


pre-commit
==========

`pre-commit <https://pre-commit.com/>`__ is configured for this project to help developers follow the coding style.
If you used ``make sync`` or ``make sync_all`` to setup your environment, it is already setup for you.
If not, you can run ``pipenv run pre-commit install`` to to install the pre-commit hooks.

You can also run ``pipenv run pre-commit run --all-files`` at any time to manually trigger these hooks.
