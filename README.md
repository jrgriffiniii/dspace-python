# DSpace Python

[![CircleCI](https://circleci.com/gh/pulibrary/dspace-python.svg?style=svg)](https://circleci.com/gh/pulibrary/dspace-python)

Python scripts for DSpace administration.

## Getting Started
### Prerequisites

- python 3.8.8
- pip
- pipenv
- make

### Installing `pipenv`

```
pyenv local 3.8.8
pip install pipenv
```

### Installing the Python package dependencies

```
pipenv shell
pipenv lock --pre
pipenv install --dev
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
