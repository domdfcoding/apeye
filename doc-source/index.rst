======
apeye
======

.. start short_desc

.. documentation-summary::
	:meta:

.. end short_desc

.. start shields

.. only:: html

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

	.. |docs| rtfd-shield::
		:project: apeye
		:alt: Documentation Build Status

	.. |docs_check| actions-shield::
		:workflow: Docs Check
		:alt: Docs Check Status

	.. |actions_linux| actions-shield::
		:workflow: Linux
		:alt: Linux Test Status

	.. |actions_windows| actions-shield::
		:workflow: Windows
		:alt: Windows Test Status

	.. |actions_macos| actions-shield::
		:workflow: macOS
		:alt: macOS Test Status

	.. |actions_flake8| actions-shield::
		:workflow: Flake8
		:alt: Flake8 Status

	.. |actions_mypy| actions-shield::
		:workflow: mypy
		:alt: mypy status

	.. |requires| image:: https://dependency-dash.repo-helper.uk/github/domdfcoding/apeye/badge.svg
		:target: https://dependency-dash.repo-helper.uk/github/domdfcoding/apeye/
		:alt: Requirements Status

	.. |coveralls| coveralls-shield::
		:alt: Coverage

	.. |codefactor| codefactor-shield::
		:alt: CodeFactor Grade

	.. |pypi-version| pypi-shield::
		:project: apeye
		:version:
		:alt: PyPI - Package Version

	.. |supported-versions| pypi-shield::
		:project: apeye
		:py-versions:
		:alt: PyPI - Supported Python Versions

	.. |supported-implementations| pypi-shield::
		:project: apeye
		:implementations:
		:alt: PyPI - Supported Implementations

	.. |wheel| pypi-shield::
		:project: apeye
		:wheel:
		:alt: PyPI - Wheel

	.. |conda-version| image:: https://img.shields.io/conda/v/domdfcoding/apeye?logo=anaconda
		:target: https://anaconda.org/domdfcoding/apeye
		:alt: Conda - Package Version

	.. |conda-platform| image:: https://img.shields.io/conda/pn/domdfcoding/apeye?label=conda%7Cplatform
		:target: https://anaconda.org/domdfcoding/apeye
		:alt: Conda - Platform

	.. |license| github-shield::
		:license:
		:alt: License

	.. |language| github-shield::
		:top-language:
		:alt: GitHub top language

	.. |commits-since| github-shield::
		:commits-since: v1.4.1
		:alt: GitHub commits since tagged version

	.. |commits-latest| github-shield::
		:last-commit:
		:alt: GitHub last commit

	.. |maintained| maintained-shield:: 2023
		:alt: Maintenance

	.. |pypi-downloads| pypi-shield::
		:project: apeye
		:downloads: month
		:alt: PyPI - Downloads

.. end shields

Overview
----------

``apeye`` provides:

* :mod:`apeye.url`: :class:`pathlib.Path`\-like objects to represent URLs
* :class:`~.Cache`: A JSON-backed cache decorator for functions
* :class:`~.RateLimitAdapter`: A CacheControl_ adapter to limit the rate of requests

.. _CacheControl: https://github.com/ionrock/cachecontrol

Installation
---------------

.. start installation

.. installation:: apeye
	:pypi:
	:github:
	:anaconda:
	:conda-channels: conda-forge, domdfcoding

.. end installation

.. attention::

	In v0.9.0 and above the :mod:`~.rate_limiter` module requires the ``limiter`` extra to be installed:

	.. prompt:: bash

		python -m pip install apeye[limiter]

API Reference
--------------

.. html-section::

.. toctree::
	:hidden:

	Home<self>

.. toctree::
	:maxdepth: 3
	:glob:

	api/url
	api/requests_url
	api/slumber_url
	api/*


.. sidebar-links::
	:caption: Links
	:github:
	:pypi: apeye

	contributing
	Source
	license


.. start links

.. only:: html

	View the :ref:`Function Index <genindex>` or browse the `Source Code <_modules/index.html>`__.

	:github:repo:`Browse the GitHub Repository <domdfcoding/apeye>`

.. end links
