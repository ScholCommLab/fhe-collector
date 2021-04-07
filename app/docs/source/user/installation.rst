.. _user_installation:

Installation
=================

.. contents:: Table of Contents
  :local:

There are different options on how to install a Python package, mostly depending
on your prefered tools and what you want to do with it. The easiest
way is in most cases to use pip (see :ref:`below <user_installation_pip>`).


.. _user_installation_requirements:

Requirements
-----------------------------

.. include:: ../snippets/requirements.rst


Installer requirements: `setuptools <https://pypi.org/project/setuptools>`_

**PostgreSQL**

First, setup a postgreSQL instance on your computer. Please look for
more information at the `PostgreSQL Website <https://www.postgresql.org>`_.

After you have set up PostgreSQL, you have to create a database for the app and give
your default user the full rights to it. In Ubuntu/Linux this works like this:

.. code-block:: shell

    USERNAME_ADMIN='YOURADMINUSERNAME'
    USERNAME_OWNER='YOUROWNERUSERNAME'
    DB_NAME='fhe_collector'
    sudo -u $USERNAME_ADMIN createdb -O $USERNAME_OWNER $DB_NAME


.. _user_installation_pip:

Pip
-----------------------------

To install the latest release of FHE Collector from PyPI, simply run this
`pip <https://pypi.org/project/pip/>`_
command in your terminal of choice:

.. include:: ../snippets/pip-install.rst


.. _user_installation_pipenv:

Pipenv
-----------------------------

`Pipenv <https://pipenv.pypa.io/en/latest/>`_ combines pip and virtualenv.

.. code-block:: shell

    pipenv install fhe_collector


.. _user_installation_source-code:

Source Code
-----------------------------

FHE Collector is actively developed on GitHub, where the code is
`always available <https://github.com/ScholCommLab/fhe-collector>`_.

You can either clone the public repository:

.. code-block:: shell

    git clone git://github.com/ScholCommLab/fhe-collector.git

Or download the archive of the ``master`` branch as a zip:

.. code-block:: shell

    curl -OL https://github.com/ScholCommLab/fhe-collector/archive/master.zip

Once you have a copy of the source, you can embed it in your own Python
package:

.. code-block:: shell

    cd fhe-collector
    pip install .


.. _user_installation_development:

Development
-----------------------------

To set up your development environment, see
:ref:`contributing_working-with-code_development-environment`.
