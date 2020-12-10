#!/bin/bash

source $DSPACE_PPPL_HOME/scripts/runit.sh

if [ "$?" != 0 ]; then
  echo 'fail'
  mutt -s 'dataspace import of pppl package failed' $DSPACE_PPPL_EMAIL  <<- EOM
    script ran on $(hostname)
    see dated log file in s3://$AWS_BUCKET/log
EOM

fi
