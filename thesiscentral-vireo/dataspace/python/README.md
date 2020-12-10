# Thesis Central (Vireo) Administration

Python administration scripts for managing integration with [Thesis Central](https://thesis-central.princeton.edu/) (an implementation of [Vireo](https://github.com/TexasDigitalLibrary/Vireo)).

## Overview

[Importing Thesis Central Submissions](./IMPORT.md)

## Getting Started

### Prerequisites

- python 3.6.9 (this may be `python3` within server environments)
- pip (this may be `pip3` within server environments)
- pipenv
- make

### Installing Dependencies

```bash
pip install pipenv
pipenv shell
pipenv lock --pre
pipenv install --dev
```

### Usage

```bash
# Building a new DSpace Simple Archive Format package (SAF)
pipenv run dspace --department="Physics" build-package
# Audit the restrictions for an SAF package
pipenv run dspace audit-restrictions --department="Physics"
# Viewing other tasks
pipenv run dspace --help
```

## Testing

```bash
pipenv install --dev
pipenv run pytest
```

## Linting

```bash
pipenv install --dev
pipenv run pylint ./**/*py
```

## Generating the Documentation

```bash
pipenv install --dev
pipenv run sphinx-build -b html -c ./ ./ _build
open _build/index.html
```
