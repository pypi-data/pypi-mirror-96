#######################
flake8-github-actions
#######################

.. start short_desc

**GitHub Actions integration for flake8.**

.. end short_desc


.. start shields

.. list-table::
	:stub-columns: 1
	:widths: 10 90

	* - Tests
	  - |actions_linux| |actions_windows| |actions_macos|
	* - PyPI
	  - |pypi-version| |supported-versions| |supported-implementations| |wheel|
	* - Activity
	  - |commits-latest| |commits-since| |maintained| |pypi-downloads|
	* - QA
	  - |codefactor| |actions_flake8| |actions_mypy| |pre_commit_ci|
	* - Other
	  - |license| |language| |requires|

.. |actions_linux| image:: https://github.com/domdfcoding/flake8-github-actions/workflows/Linux/badge.svg
	:target: https://github.com/domdfcoding/flake8-github-actions/actions?query=workflow%3A%22Linux%22
	:alt: Linux Test Status

.. |actions_windows| image:: https://github.com/domdfcoding/flake8-github-actions/workflows/Windows/badge.svg
	:target: https://github.com/domdfcoding/flake8-github-actions/actions?query=workflow%3A%22Windows%22
	:alt: Windows Test Status

.. |actions_macos| image:: https://github.com/domdfcoding/flake8-github-actions/workflows/macOS/badge.svg
	:target: https://github.com/domdfcoding/flake8-github-actions/actions?query=workflow%3A%22macOS%22
	:alt: macOS Test Status

.. |actions_flake8| image:: https://github.com/domdfcoding/flake8-github-actions/workflows/Flake8/badge.svg
	:target: https://github.com/domdfcoding/flake8-github-actions/actions?query=workflow%3A%22Flake8%22
	:alt: Flake8 Status

.. |actions_mypy| image:: https://github.com/domdfcoding/flake8-github-actions/workflows/mypy/badge.svg
	:target: https://github.com/domdfcoding/flake8-github-actions/actions?query=workflow%3A%22mypy%22
	:alt: mypy status

.. |requires| image:: https://requires.io/github/domdfcoding/flake8-github-actions/requirements.svg?branch=master
	:target: https://requires.io/github/domdfcoding/flake8-github-actions/requirements/?branch=master
	:alt: Requirements Status

.. |codefactor| image:: https://img.shields.io/codefactor/grade/github/domdfcoding/flake8-github-actions?logo=codefactor
	:target: https://www.codefactor.io/repository/github/domdfcoding/flake8-github-actions
	:alt: CodeFactor Grade

.. |pypi-version| image:: https://img.shields.io/pypi/v/flake8-github-actions
	:target: https://pypi.org/project/flake8-github-actions/
	:alt: PyPI - Package Version

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/flake8-github-actions?logo=python&logoColor=white
	:target: https://pypi.org/project/flake8-github-actions/
	:alt: PyPI - Supported Python Versions

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/flake8-github-actions
	:target: https://pypi.org/project/flake8-github-actions/
	:alt: PyPI - Supported Implementations

.. |wheel| image:: https://img.shields.io/pypi/wheel/flake8-github-actions
	:target: https://pypi.org/project/flake8-github-actions/
	:alt: PyPI - Wheel

.. |license| image:: https://img.shields.io/github/license/domdfcoding/flake8-github-actions
	:target: https://github.com/domdfcoding/flake8-github-actions/blob/master/LICENSE
	:alt: License

.. |language| image:: https://img.shields.io/github/languages/top/domdfcoding/flake8-github-actions
	:alt: GitHub top language

.. |commits-since| image:: https://img.shields.io/github/commits-since/domdfcoding/flake8-github-actions/v0.1.1
	:target: https://github.com/domdfcoding/flake8-github-actions/pulse
	:alt: GitHub commits since tagged version

.. |commits-latest| image:: https://img.shields.io/github/last-commit/domdfcoding/flake8-github-actions
	:target: https://github.com/domdfcoding/flake8-github-actions/commit/master
	:alt: GitHub last commit

.. |maintained| image:: https://img.shields.io/maintenance/yes/2021
	:alt: Maintenance

.. |pypi-downloads| image:: https://img.shields.io/pypi/dm/flake8-github-actions
	:target: https://pypi.org/project/flake8-github-actions/
	:alt: PyPI - Downloads

.. |pre_commit_ci| image:: https://results.pre-commit.ci/badge/github/domdfcoding/flake8-github-actions/master.svg
	:target: https://results.pre-commit.ci/latest/github/domdfcoding/flake8-github-actions/master
	:alt: pre-commit.ci status

.. end shields

Installation
--------------

.. start installation

``flake8-github-actions`` can be installed from PyPI.

To install with ``pip``:

.. code-block:: bash

	$ python -m pip install flake8-github-actions

.. end installation

Use with GitHub Actions
----------------------------

Example workflow:

.. code-block:: yaml

	---

	name: Flake8

	on:
	  push:
	  pull_request:
	    branches: ["master"]

	jobs:
	  Run:
	    name: "Flake8"
	    runs-on: "ubuntu-18.04"

	    steps:
	      - name: Checkout 🛎️
	        uses: "actions/checkout@v2"

	      - name: Setup Python 🐍
	        uses: "actions/setup-python@v2"
	        with:
	          python-version: "3.8"

	      - name: Install dependencies 🔧
	        run: |
	          python -VV
	          python -m site
	          python -m pip install --upgrade pip setuptools wheel
	          python -m pip install flake8
	          python -m pip install flake8-github-actions

	      - name: "Run Flake8"
	        run: "flake8 --format github"
