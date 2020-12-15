# Princeton Plasma Physics Laboratory Collection Management

Administration utilities for managing the [Princeton Plasma Physics Laboratory Collection](https://dataspace.princeton.edu/jspui/handle/88435/dsp01pz50gz45g) in [DataSpace](https://dataspace.princeton.edu/jspui/).

## Getting Started

### Prerequisites

- python 3.6.9 (this may be `python3` within server environments)
- pip (this may be `pip3` within server environments)
- pipenv
- make

### Installing `pipenv`

```bash
pyenv local 3.6.9
pip install pipenv
```

### Installing the Python package dependencies

#### 3.6.9

```bash
pipenv --python 3.6.9 shell
pipenv lock --pre
pipenv install --dev
```
### Install and Configure the AWS CLI
*This is intended to be installed and run on the server environment:*

```bash
pip install --user awscli
```

Please ensure that the following configuration files are in place for AWS in `$HOME/.aws/credentials`:

```bash
[default]
aws_access_key_id = [ACCESS_KEY_ID]
aws_secret_access_key = [SECRET_ACCESS_KEY]
aws_region = us-east-1
```

The following should also be in place with `$HOME/.aws/config`:

```bash
[default]
region = us-east-1
```

Alternatively, should access fail, please explicitly declare the BASH environment variables:

```bash
export AWS_ACCESS_KEY_ID=[ACCESS_KEY_ID]
export AWS_SECRET_ACCESS_KEY=[SECRET_ACCESS_KEY]
export AWS_DEFAULT_REGION=us-east-1
```

## Usage

```bash
pipenv run pppl sync \
  --s3-mount-point=dspace_imports
```

```bash
pipenv run pppl ingest \
  --s3-mount-point=dspace_imports \
  --dspace-submitter=admin@institution.edu \
  --dspace-home=/dspace
```

```bash
export DSPACE_HOME=/dspace
export DSPACE_PPPL_HOME=$HOME/pulibrary-src/dspace-python/pppl
export LOG_LEVEL=DEBUG

export DSPACE_AWS_S3=$DSPACE_PPPL_HOME/s3
export AWS_BUCKET=pppldataspace

export DSPACE_EPERSON="pppldataspace@princeton.edu"
export DSPACE_PPPL_EMAIL="jrg5@princeton.edu"
```
