#!/bin/bash

export DATASPACE_IMPORT=$DSPACE_PPPL_HOME/dataspace_import.py

export S3_LOGDIR=$DSPACE_AWS_S3/log
export DATE=`date "+%Y/%m"`
export LONG_DATE=`date "+%Y-%m-%d:%H:%M"`
export IMPORT_LOG_DIR=$S3_LOGDIR/$DATE
export IMPORT_LOG_FILE=$IMPORT_LOG_DIR/$LONG_DATE-s3-bucket.log

mkdir -p $IMPORT_LOG_DIR
touch $IMPORT_LOG_FILE

# This synchronizes from S3 to the local file system
echo  "Logging to $IMPORT_LOG_FILE"
echo "aws s3 sync s3://$AWS_BUCKET $DSPACE_AWS_S3 >> $IMPORT_LOG_FILE"
aws s3 sync s3://$AWS_BUCKET $DSPACE_AWS_S3 >> $IMPORT_LOG_FILE

# export DSPACE_PPPL_HOME=$HOME/pulibrary-src/dspace-python/pppl
# export DSPACE_AWS_S3=$DSPACE_PPPL_HOME/s3
# export AWS_BUCKET=pppldataspace

# echo "aws s3 sync $DSPACE_AWS_S3/imports s3://$AWS_BUCKET/imports"
# aws s3 sync $DSPACE_AWS_S3/imports s3://$AWS_BUCKET/imports

# This uploads any new SIPs
echo "python $DATASPACE_IMPORT $DSPACE_HOME $DSPACE_EPERSON $DSPACE_AWS_S3 >> $IMPORT_LOG_FILE"
python $DATASPACE_IMPORT $DSPACE_HOME $DSPACE_EPERSON $DSPACE_AWS_S3 >> $IMPORT_LOG_FILE

echo "---"
cat $IMPORT_LOG_FILE
