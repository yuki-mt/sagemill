#!/bin/bash

run_type=$1

if [ "$run_type" == "train" ] ; then
  # change JSON to arguments
  # e.g. {"foo": 1, "fuga": "xx"} -> --foo 1 --fuga xx
  args=`cat /opt/ml/input/config/hyperparameters.json \
    | jq -r 'keys[] as $k | "--\($k) \(.[$k])"' | tr '\n' ' '`
  python entrypoint.py $args
else
  echo "The argument '$run_type' is not supported"
fi
