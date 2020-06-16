# DSpace Python

[![CircleCI](https://circleci.com/gh/pulibrary/dspace-python.svg?style=svg)](https://circleci.com/gh/pulibrary/dspace-python)

Python scripts for DSpace administration.

## Getting Started

## Prerequisites

- python 3.8.3
- pip
- pipenv
- make

### Installing `pipenv`

```
pip install pipenv
```

### Installing the Python package dependencies

```
pipenv shell
pipenv lock --pre
pipenv install
```

## Development

### Building Documentation

```
pipenv run sphinx-build -b html source build/html
```

or

```
make html
```
