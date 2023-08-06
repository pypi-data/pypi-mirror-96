========
Overview
========

An example package. Generated with cookiecutter-pylibrary.

* Free software: MIT license

Installation
============

::

    pip install dnf-converter

You can also install the in-development version with::

    pip install git+ssh://git@https://github.com/christe90/dnf_converter.git/christe90/python-dnf_converter.git@master

Documentation
=============


https://python-dnf_converter.readthedocs.io/


Development
===========

To run all the tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
