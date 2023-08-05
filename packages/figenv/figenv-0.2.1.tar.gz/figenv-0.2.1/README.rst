Figenv
======

.. image:: https://github.com/gtmanfred/figenv/workflows/Tests/badge.svg
    :target: https://github.com/gtmanfred/figenv

.. image:: https://img.shields.io/codecov/c/github/gtmanfred/figenv
    :target: https://codecov.io/gh/gtmanfred/figenv

.. image:: https://img.shields.io/pypi/v/figenv
    :target: https://pypi.org/project/figenv

.. image:: https://img.shields.io/pypi/l/figenv
    :target: http://www.apache.org/licenses/LICENSE-2.0

.. image:: https://img.shields.io/pypi/dm/figenv
    :target: https://pypi.org/project/figenv/

Metaclass for handling configuration class objects using environment variables.

If an environment variable is specified, the metaclass will pull the variable
from the environment, the variable defined on the class will be used.

This was built to be a dropin replacement for `flask-env
<https://pypi.org/project/Flask-Env/>`_ but supporting change environment
variables after the meta class is loaded.

Config
------

There are 2 configuration options, that are set on the base class object.

``ENV_LOAD_ALL = <True/False>``

   Setting this on the class will allow loading any environment variable even
   if it is not set on the base class.

``ENV_PREFIX = <string>``

   Setting this will will be a prefix for variables in the environment.

Install
-------

This should just be pip installed

.. code-block:: bash

   python3 -m pip install figenv

Usage
-----

The basic usecase is below.

.. code-block:: python

    import os

    import figenv

    class Config(metaclass=figenv.MetaConfig):

        ENV_LOAD_ALL = True
        ENV_PREFIX = 'ROCKSTEADY_'

        BLAH = True
        TIMEOUT = 5
        POSTGRES_HOST = 'localhost'
        POSTGRES_PORT = 5432
        POSTGRES_USER = 'bebop'
        POSTGRES_PASS = 'secret'
        POSTGRES_DB = 'main'

        def SQLALCHEMY_DATABASE_URI(cls):
            return 'postgresql://{user}:{secret}@{host}:{port}/{database}?sslmode=require'.format(
                user=cls.POSTGRES_USER,
                secret=cls.POSTGRES_PASS,
                host=cls.POSTGRES_HOST,
                port=cls.POSTGRES_PORT,
                database=cls.POSTGRES_DATABASE,
            )

   assert Config.TIMEOUT == 5
   assert Config.BLAH is True
   assert Config.SQLALCHEMY_DATABASE_URI == 'postgresql://bebop:secret@localhost:5432/public?sslmode=require'
   try:
       Config.WHAT
   except AttributeError:
       pass

   os.environ.update({
       'ROCKSTEADY_BLAH': 'false',
       'ROCKSTEADY_TIMEOUT': '15',
       'ROCKSTEADY_WHAT': '2.9',
       'ROCKSTEADY_SQLALCHEMY_DATABASE_URI': 'postgres://localhost:5432/db',
   })

   assert Config.TIMEOUT == 15
   assert Config.BLAH is False
   assert Config.WHAT == 2.9
   assert Config.SQLALCHEMY_DATABASE_URI == 'postgres://localhost:5432/db'
