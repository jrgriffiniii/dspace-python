# DSpace Python

[![CircleCI](https://circleci.com/gh/pulibrary/dspace-python.svg?style=svg)](https://circleci.com/gh/pulibrary/dspace-python)

Python scripts for DSpace administration.

## Getting Started

## Prerequisites

- python 3.8.3 or python 2.7.18
- pip
- pipenv
- make

### Installing `pipenv`

```
# For Python 3.x support:
pyenv local 3.8.3

# Or, for legacy support:
pyenv local 2.7.18

pip install pipenv
```

### Installing the Python package dependencies

#### 3.8.3

```
pipenv --python 2.7.18 shell
pipenv lock --pre
pipenv install
```

#### 2.7.18

```
cp Pipfile.legacy Pipfile
cp Pipfile.lock.legacy Pipfile.lock
pipenv --python 2.7.18 shell
pipenv lock --pre
pipenv install
```

### Usage

- [Thesis Central and Senior Theses Administration](./thesiscentral-vireo/dataspace/python/README.md)

## Development

### Building Documentation

```
pipenv run sphinx-build -b html source build/html
```

or

```
make html
```
