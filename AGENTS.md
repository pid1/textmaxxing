# AGENTS.md

## Sadr

### Build and test
- The repo has no tests. Run `uv sync --locked` and then `uv run python -c "import main"`. Both pass when the lockfile matches pyproject.toml and the app loads. The import needs no network and no API key.

### Toolchain
- Python 3.15 (`.python-version`) with uv. Dependencies live in `pyproject.toml` and `uv.lock`.
