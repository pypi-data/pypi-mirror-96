========
p_config
========


.. image:: https://img.shields.io/pypi/v/p_config.svg
        :target: https://pypi.python.org/pypi/p_config

.. image:: https://img.shields.io/travis/zlqm/p_config.svg
        :target: https://travis-ci.com/zlqm/p_config

.. image:: https://readthedocs.org/projects/p-config/badge/?version=latest
        :target: https://p-config.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status



Simple configure management tool for python project.

YAML file and environment variable both supported.


* Free software: BSD license
* Documentation: https://p-config.readthedocs.io.


Install
-------

.. code:: bash

   $: pip install p_config --upgrade


Usage
-----

1. Initialize a `Config` instance. You can add some default value here.
2. Load local file or environment value. Value with same key will be overridden.
3. Access config through the instance


.. code:: python

    (default) p_config ) ENV=UAT ipython
    Python 3.9.1 (default,)
    Type 'copyright', 'credits' or 'license' for more information
    IPython 7.20.0 -- An enhanced Interactive Python. Type '?' for help.

    In [1]: from p_config import Config

    In [2]: config = Config(ENV='SIT')

    In [3]: config.ENV  # default config defined at [2]
    Out[3]: 'SIT'

    In [4]: !cat demo.yaml
    ENV: PRD
    BROKER_URI: redis://
    DB:
      NAME: test
      HOST: localhost
      PORT: 3306

    In [5]: config.load_yaml_file('demo.yaml')

    In [6]: config.ENV  # overridden by config in demo.yaml
    Out[6]: 'PRD'

    In [7]: config.DB  # only support upper case 
    Out[7]: {'NAME': 'test', 'HOST': 'localhost', 'PORT': 3306}

    In [8]: config.DB.HOST
    Out[8]: 'localhost'

    In [9]: config.load_env()

    In [10]: config.ENV  # overridden by config in demo.yaml
    Out[10]: 'UAT'


Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
