# Contributing

## Local setup

Use Python 3.9 or newer:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[test]" build
```

## Verification

Run every check before opening a pull request:

```bash
python -m pytest -q
python -m build
```

The wheel must contain `agent_category_theory.py`, and importing that module
from outside the repository root must succeed after installing the wheel.

## Pull requests

- Keep changes focused and backward compatible where practical.
- Add tests for changed behavior and edge cases.
- Update the README when public behavior changes.
- Do not commit credentials, generated distributions, virtual environments, or
  test caches.
- Explain the problem, approach, verification, and compatibility impact in the
  pull-request description.

By contributing, you agree that your contribution is licensed under the MIT
License in this repository.