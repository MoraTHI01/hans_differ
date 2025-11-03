#!/bin/bash

scriptDir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

username=""
password=""

while getopts up flag
do
  case "${flag}" in
    u) username="$OPTARG";;
    p) password="$OPTARG";;
  esac
done

if [[ ! -f $scriptDir/.env.config ]]
then
  echo "No .env.config file provided - defaults from .env.template will be used"
  cp $scriptDir/.env.template $scriptDir/.env.config
fi

if [[ ! -d $scriptDir/report  ]]
then
  mkdir $scriptDir/report
fi

# Filename in format YYYY-MM-DD_HH-mm-SS.html
reportFilename=$(date +"%F_%H-%M-%S").html

docker run \
-v $scriptDir/locustfile.py:/home/locust/locustfile.py \
-v $scriptDir/report:/home/locust/report \
-e LOAD_TEST_USERNAME="$username" \
-e LOAD_TEST_PASSWORD="$password" \
--env-file $scriptDir/.env.config \
locustio/locust --headless --html report/$reportFilename
