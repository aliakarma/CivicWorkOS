# Setup

## Requirements

- Python 3.10-3.12 (tested on 3.11.9)
- No GPU, no external services, no database

## From a clean environment

```bash
git clone <this-repository>
cd Github   # or wherever you placed this repository's contents
pip install -e ".[dev]"
```

This installs `civicworkos` in editable mode plus its three runtime
dependencies (`pydantic`, `PyYAML`, `PuLP`) and dev tools (`pytest`, `ruff`,
`mypy`). `PuLP` ships its own CBC solver binary, so no separate MIP solver
installation is required on Windows, macOS, or Linux.

If you only need to run the library (no tests/linting), use:

```bash
pip install -e .
```

or, without an editable install:

```bash
pip install -r requirements.txt
```

## Verify the installation

Run the repository's one ground-truth check — it recomputes every checkable
number in the paper's worked example (sec:worked) and analytic model (sec:cadmodel, fig:cad-trend)
independently from the article's own stated inputs:

```bash
python scripts/verify_worked_example.py
```

Expected final line: `All worked-example numbers reproduced within
tolerance.` and exit code `0`. If this fails, something is wrong with your
environment or a regression has been introduced — see
[troubleshooting.md](troubleshooting.md).

## Run the test suite

```bash
pytest tests/ -v
```

All tests should pass in a few seconds on a typical laptop (the CLI smoke
tests spawn subprocesses and dominate the wall-clock time; see
[SMOKE_TEST_REPORT.md](../SMOKE_TEST_REPORT.md) for the actual observed
runtime and environment).

## Docker

```bash
docker build -t civicworkos .
docker run --rm civicworkos
```

The default entrypoint runs `scripts/verify_worked_example.py`. Override to
run any other script, e.g.:

```bash
docker run --rm civicworkos python scripts/run_simulation.py 200 42
```

## Optional: linting and type checking

```bash
ruff check src/ sim/ scripts/ tests/
mypy src/civicworkos
```

Both are clean on the repository as delivered (see
[SMOKE_TEST_REPORT.md](../SMOKE_TEST_REPORT.md)).
