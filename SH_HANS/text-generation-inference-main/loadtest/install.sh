#!/bin/bash

if [[ ! -f "train-v2.0.json" ]]
then
  echo "Downloading SQuAD training set v2.0 from https://rajpurkar.github.io/SQuAD-explorer licensed under CC-BY-4.0-SA http://creativecommons.org/licenses/by-sa/4.0/legalcode"
  wget https://rajpurkar.github.io/SQuAD-explorer/dataset/train-v2.0.json
fi
