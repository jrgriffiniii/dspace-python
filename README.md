# DSpace Python

[![CircleCI](https://circleci.com/gh/pulibrary/dspace-python.svg?style=svg)](https://circleci.com/gh/pulibrary/dspace-python)

Python scripts for DSpace administration.

## Getting Started

## Prerequisites

- python 3.6.9 (this may be `python3` within server environments)
- pip (this may be `pip3` within server environments)
- pipenv
- make

### Installing `pipenv`

```
pyenv local 3.6.9
pip install pipenv
```

### Installing the Python package dependencies

#### 3.6.9

```
pipenv --python 3.6.9 shell
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
