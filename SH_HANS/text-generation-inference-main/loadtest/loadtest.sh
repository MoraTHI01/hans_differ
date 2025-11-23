#!/bin/bash

python3 loadtest.py -s 127.0.0.1 -p 8080 -i train-v2.0.json -n 16
if [[ $? -gt 0 ]]
then
    "Unexpected error during loadtest.py occured!"
    exit 1
fi

python3 loadtest.py -s 127.0.0.1 -p 8080 -i train-v2.0.json -n 32
if [[ $? -gt 0 ]]
then
    "Unexpected error during loadtest.py occured!"
    exit 1
fi

python3 loadtest.py -s 127.0.0.1 -p 8080 -i train-v2.0.json -n 64
if [[ $? -gt 0 ]]
then
    "Unexpected error during loadtest.py occured!"
    exit 1
fi

python3 loadtest.py -s 127.0.0.1 -p 8080 -i train-v2.0.json -n 128
if [[ $? -gt 0 ]]
then
    "Unexpected error during loadtest.py occured!"
    exit 1
fi

python3 loadtest.py -s 127.0.0.1 -p 8080 -i train-v2.0.json -n 256
if [[ $? -gt 0 ]]
then
    "Unexpected error during loadtest.py occured!"
    exit 1
fi
