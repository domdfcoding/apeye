======
apeye
======

.. start short_desc

**Handy tools for working with URLs and APIs.**

.. end short_desc


.. start shields

.. list-table::
	:stub-columns: 1
	:widths: 10 90

	* - Docs
	  - |docs| |docs_check|
	* - Tests
	  - |actions_linux| |actions_windows| |actions_macos| |coveralls|
	* - PyPI
	  - |pypi-version| |supported-versions| |supported-implementations| |wheel|
	* - Anaconda
	  - |conda-version| |conda-platform|
	* - Activity
	  - |commits-latest| |commits-since| |maintained| |pypi-downloads|
	* - QA
	  - |codefactor| |actions_flake8| |actions_mypy|
	* - Other
	  - |license| |language| |requires|

.. |docs| image:: https://img.shields.io/readthedocs/apeye/latest?logo=read-the-docs
	:target: https://apeye.readthedocs.io/en/latest
	:alt: Documentation Build Status

.. |docs_check| image:: https://github.com/domdfcoding/apeye/workflows/Docs%20Check/badge.svg
	:target: https://github.com/domdfcoding/apeye/actions?query=workflow%3A%22Docs+Check%22
	:alt: Docs Check Status

.. |actions_linux| image:: https://github.com/domdfcoding/apeye/workflows/Linux/badge.svg
	:target: https://github.com/domdfcoding/apeye/actions?query=workflow%3A%22Linux%22
	:alt: Linux Test Status

.. |actions_windows| image:: https://github.com/domdfcoding/apeye/workflows/Windows/badge.svg
	:target: https://github.com/domdfcoding/apeye/actions?query=workflow%3A%22Windows%22
	:alt: Windows Test Status

.. |actions_macos| image:: https://github.com/domdfcoding/apeye/workflows/macOS/badge.svg
	:target: https://github.com/domdfcoding/apeye/actions?query=workflow%3A%22macOS%22
	:alt: macOS Test Status

.. |actions_flake8| image:: https://github.com/domdfcoding/apeye/workflows/Flake8/badge.svg
	:target: https://github.com/domdfcoding/apeye/actions?query=workflow%3A%22Flake8%22
	:alt: Flake8 Status

.. |actions_mypy| image:: https://github.com/domdfcoding/apeye/workflows/mypy/badge.svg
	:target: https://github.com/domdfcoding/apeye/actions?query=workflow%3A%22mypy%22
	:alt: mypy status

.. |requires| image:: https://dependency-dash.repo-helper.uk/github/domdfcoding/apeye/badge.svg
	:target: https://dependency-dash.repo-helper.uk/github/domdfcoding/apeye/
	:alt: Requirements Status

.. |coveralls| image:: https://img.shields.io/coveralls/github/domdfcoding/apeye/master?logo=coveralls
	:target: https://coveralls.io/github/domdfcoding/apeye?branch=master
	:alt: Coverage

.. |codefactor| image:: https://img.shields.io/codefactor/grade/github/domdfcoding/apeye?logo=codefactor
	:target: https://www.codefactor.io/repository/github/domdfcoding/apeye
	:alt: CodeFactor Grade

.. |pypi-version| image:: https://img.shields.io/pypi/v/apeye
	:target: https://pypi.org/project/apeye/
	:alt: PyPI - Package Version

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/apeye?logo=python&logoColor=white
	:target: https://pypi.org/project/apeye/
	:alt: PyPI - Supported Python Versions

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/apeye
	:target: https://pypi.org/project/apeye/
	:alt: PyPI - Supported Implementations

.. |wheel| image:: https://img.shields.io/pypi/wheel/apeye
	:target: https://pypi.org/project/apeye/
	:alt: PyPI - Wheel

.. |conda-version| image:: https://img.shields.io/conda/v/domdfcoding/apeye?logo=anaconda
	:target: https://anaconda.org/domdfcoding/apeye
	:alt: Conda - Package Version

.. |conda-platform| image:: https://img.shields.io/conda/pn/domdfcoding/apeye?label=conda%7Cplatform
	:target: https://anaconda.org/domdfcoding/apeye
	:alt: Conda - Platform

.. |license| image:: https://img.shields.io/github/license/domdfcoding/apeye
	:target: https://github.com/domdfcoding/apeye/blob/master/LICENSE
	:alt: License

.. |language| image:: https://img.shields.io/github/languages/top/domdfcoding/apeye
	:alt: GitHub top language

.. |commits-since| image:: https://img.shields.io/github/commits-since/domdfcoding/apeye/v1.4.0
	:target: https://github.com/domdfcoding/apeye/pulse
	:alt: GitHub commits since tagged version

.. |commits-latest| image:: https://img.shields.io/github/last-commit/domdfcoding/apeye
	:target: https://github.com/domdfcoding/apeye/commit/master
	:alt: GitHub last commit

.. |maintained| image:: https://img.shields.io/maintenance/yes/2023
	:alt: Maintenance

.. |pypi-downloads| image:: https://img.shields.io/pypi/dm/apeye
	:target: https://pypi.org/project/apeye/
	:alt: PyPI - Downloads

.. end shields

``apeye`` provides:

* ``pathlib.Path``\-like objects to represent URLs
* a JSON-backed cache decorator for functions
* a CacheControl_ adapter to limit the rate of requests

See `the documentation`_ for more details.

.. _CacheControl: https://github.com/ionrock/cachecontrol
.. _the documentation: https://apeye.readthedocs.io/en/latest/api/cache.html

Installation
--------------

.. start installation

``apeye`` can be installed from PyPI or Anaconda.

To install with ``pip``:

.. code-block:: bash

	$ python -m pip install apeye

To install with ``conda``:

	* First add the required channels

	.. code-block:: bash

		$ conda config --add channels https://conda.anaconda.org/conda-forge
		$ conda config --add channels https://conda.anaconda.org/domdfcoding

	* Then install

	.. code-block:: bash

		$ conda install apeye

.. end installation


.. attention::

	In v0.9.0 and above the ``rate_limiter`` module requires the ``limiter`` extra to be installed:

	.. code-block:: bash

		$ python -m pip install apeye[limiter]
