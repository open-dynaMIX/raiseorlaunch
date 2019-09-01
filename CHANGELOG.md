# v2.3.2

## Fixes
 - [tests] fix i3ipc socket mock


# v2.3.1

## Features
 - Run tests with py37, py38 and pypy3
 - Merge `.coveragerc`, `.flake8` and `.isort.cfg` into `setup.cfg`
 - Add `LICENSE.txt`, tests and `tox.ini` to sdist


# v2.3.0

## Features
 - Add tests with 100% coverage
 - Introduce [black](https://github.com/python/black)
 - Introduce [isort](https://github.com/timothycrosley/isort)
 - Introduce [flake8](https://gitlab.com/pycqa/flake8)
 - Use Travis CI to ensure and enforce all of the above


# v2.2.1

## Fixes
 - `--leave-fullscreen` doesn't work if no workspace has been provided #30


# v2.2.0

## Features
 - Add flag to disable existing fullscreen #27
 - Rename --init-workspace to --target-workspace #28


# v2.1.0

## Features
 - Added flag to set initial workspace #15
 - Move created windows to expected workspace #16
 - Window cycling #17
 - Use the new `timeout` argument for i3ipc main loop #19
 - Move to markdown for README #23
