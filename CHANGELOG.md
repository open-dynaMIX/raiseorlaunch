## v2.3.5

### Fix
* Only retain workspace_back_and_forth if workspace is set ([`d8ae56f`](https://github.com/open-dynaMIX/raiseorlaunch/commit/d8ae56fd382705eaa6fa2d0648a12526e0a86035))


## v2.3.4

### Fixes
 - handle empty window properties (4679401e2858c261bc5b403cdd04644019b8508e)


## v2.3.3

### Fixes
 - We do no longer automatically move windows to the workspace we think it belongs,
   because that interfered with i3s `assign`. #38


## v2.3.2

### Fixes
 - [tests] fix i3ipc socket mock


## v2.3.1

### Features
 - Run tests with py37, py38 and pypy3
 - Merge `.coveragerc`, `.flake8` and `.isort.cfg` into `setup.cfg`
 - Add `LICENSE.txt`, tests and `tox.ini` to sdist


## v2.3.0

### Features
 - Add tests with 100% coverage
 - Introduce [black](https://github.com/python/black)
 - Introduce [isort](https://github.com/timothycrosley/isort)
 - Introduce [flake8](https://gitlab.com/pycqa/flake8)
 - Use Travis CI to ensure and enforce all of the above


## v2.2.1

### Fixes
 - `--leave-fullscreen` doesn't work if no workspace has been provided #30


## v2.2.0

### Features
 - Add flag to disable existing fullscreen #27
 - Rename --init-workspace to --target-workspace #28


## v2.1.0

### Features
 - Added flag to set initial workspace #15
 - Move created windows to expected workspace #16
 - Window cycling #17
 - Use the new `timeout` argument for i3ipc main loop #19
 - Move to markdown for README #23
