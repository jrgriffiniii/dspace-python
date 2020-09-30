# Thesis Central (Vireo) Administration

Python administration scripts for managing integration with [Thesis Central](https://thesis-central.princeton.edu/) (an implementation of [Vireo](https://github.com/TexasDigitalLibrary/Vireo)).

## Overview

[Importing Thesis Central Submissions](./IMPORT.md)

## Getting Started

```
% python --version
Python 2.7.17
```

### Installing Dependencies

```bash
% pip install pipenv
% pipenv shell --python 2.7.17
% pipenv install
```

### Usage

```bash
# Building a new DSpace Simple Archive Format package (SAF)
% pipenv run dspace --department="Physics" build-package
# Audit the restrictions for an SAF package
% pipenv run dspace audit-restrictions --department="Physics"
% pipenv run dspace --help
```

## Development

### Testing

```bash
% pipenv install --dev
% pipenv run pytest
```

### Linting

```bash
% pipenv install --dev
% pipenv run pylint ./**/*py
```

### Generate the Documentation

```bash
% pipenv install --dev
% pipenv run sphinx-build -b html -c ./ ./ _build
% open _build/index.html
```
