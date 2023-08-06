# flake8-pytest-importorskip

[![pypi](https://badge.fury.io/py/flake8-pytest-importorskip.svg)](https://pypi.org/project/flake8-pytest-importorskip)
[![Python: 3.6+](https://img.shields.io/badge/Python-3.6+-blue.svg)](https://pypi.org/project/flake8-pytest-importorskip)
[![Downloads](https://img.shields.io/pypi/dm/flake8-pytest-importorskip.svg)](https://pypistats.org/packages/flake8-pytest-importorskip)
![Build Status](https://img.shields.io/github/checks-status/ashb/flake8-pytest-importorskip/main)
[![Code coverage](https://codecov.io/gh/ashb/flake8-pytest-importorskip/branch/main/graph/badge.svg)](https://codecov.io/gh/ashb/flake8-pytest-importorskip)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-green.svg)](https://en.wikipedia.org/wiki/Apache_License)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

## Description

Treat `pytest.importorskip` as an import statement, not code, to silence the "module level import not at top of file" (E402) from pycodestyle

It allows code such as this to pass without having to globally disable E402.

It does this in a _slightly_ hacky way (see the docs of [kgb] for details) , so it may break in future versions of pycodestyle.

### Checks:

None

## Installation

    pip install flake8-pytest-importorskip

## Usage

`flake8 <your code>`

## For developers

### Create venv and install deps

    make init

### Install git precommit hook

    make precommit_install

### Run linters, autoformat, tests etc.

    make pretty lint test

### Bump new version

    make bump_major
    make bump_minor
    make bump_patch

## License

Apache 2.0

[kgb]: https://github.com/beanbaginc/kgb

## Change Log

Unreleased
-----

* ...

1.1.0 - 2021-03-01
-----

* Replace accessing private state of flake8 plugins with wrapping/spying on function, using [kgb]

1.0.0 - 2021-02-19
-----

* initial
