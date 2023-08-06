[![Build Status](https://github.com/MarcoGorelli/absolufy-imports/workflows/tox/badge.svg)](https://github.com/MarcoGorelli/absolufy-imports/actions?workflow=tox)
[![Coverage](https://codecov.io/gh/MarcoGorelli/absolufy-imports/branch/main/graph/badge.svg)](https://codecov.io/gh/MarcoGorelli/absolufy-imports)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/MarcoGorelli/absolufy-imports/main.svg)](https://results.pre-commit.ci/latest/github/MarcoGorelli/absolufy-imports/main)

absolufy-imports
===========

A tool and pre-commit hook to automatically convert relative imports to absolute.

<p align="center">
    <a href="#readme">
        <img alt="demo" src="https://raw.githubusercontent.com/nbQA-dev/nbQA-demo/master/abs-imports.gif">
    </a>
</p>

## Installation

```
pip install absolufy-imports
```

## Usage as a pre-commit hook

See [pre-commit](https://github.com/pre-commit/pre-commit) for instructions

Sample `.pre-commit-config.yaml`:

```yaml
-   repo: https://github.com/MarcoGorelli/absolufy-imports
    rev: v0.2.2
    hooks:
    -   id: absolufy-imports
```

## Command-line example

```console
$ cat mypackage/myfile.py
from . import __version__
$ absolufy-imports mypackage/myfile.py
$ cat mypackage/myfile.py
from mypackage import __version__
```

If your package follows the popular `./src` layout, you can pass your application directories via `--application-directories`, e.g.

```console
$ cat src/mypackage/myfile.py
from . import __version__
$ absolufy-imports src/mypackage/myfile.py --application-directories src
$ cat src/mypackage/myfile.py
from mypackage import __version__
```

Multiple application directories should be comma-separated, e.g. `--application-directories .:src`. This is the same as in [reorder-python-imports](https://github.com/asottile/reorder_python_imports).

## See also

Check out [pyupgrade](https://github.com/asottile/pyupgrade), which I learned a lot from when writing this.
