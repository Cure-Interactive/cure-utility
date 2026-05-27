# Cure Utility

Shared Python utility helpers used by Cure Interactive scripts.

## Package Layout

- `cure_utility/__init__.py`: utility classes for paths, configuration, terminal formatting, logging, prompts, progress, and small test helpers
- `setup.py`: package metadata for editable installs
- `install_package.py`: local editable-install helper

## Install

From this repository:

```bash
python -m pip install -e .
```

Or run the helper:

```bash
python install_package.py
```

## Verify

```bash
python -m pip show cure_utility
```

This package is primarily maintained as support code for the standalone Cure utility scripts.
