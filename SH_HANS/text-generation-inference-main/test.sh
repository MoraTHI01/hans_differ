#!/bin/bash

test_dir="test"
connection=127.0.0.1:8080
mkdir -p $test_dir

curl $connection/generate \
    -X POST \
    -d '{"inputs":"What is Deep Learning?","parameters":{"max_new_tokens":64}}' \
    -H 'Content-Type: application/json' > $test_dir/test_result_01.json

curl $connection/generate \
    -X POST \
    -d '{"inputs":"Wie hoch ist der Eiffelturm?","parameters":{"max_new_tokens":64}}' \
    -H 'Content-Type: application/json' > $test_dir/test_result_02.json

curl $connection/generate \
    -X POST \
    -d '{"inputs":"Can you write in german?","parameters":{"max_new_tokens":64}}' \
    -H 'Content-Type: application/json' > $test_dir/test_result_03.json

curl $connection/generate \
    -X POST \
    -d '{"inputs":"Who is Albert Einstein and what is his biggest contribution to science?","parameters":{"max_new_tokens":64}}' \
    -H 'Content-Type: application/json' > $test_dir/test_result_04.json


system_prompt="### System:\\nYour name is HAnSi. HAnSi is an AI that follows instructions extremely well. Help as much as you can. Remember, be safe, and don't do anything illegal.\\n\\n"


message="Write a poem please."
prompt='{"inputs": "'${system_prompt}'### Human: '${message}'\\n\\n### Assistant:\\n","parameters":{"max_new_tokens":64}}'

curl $connection/generate \
    -X POST \
    -d "$prompt" \
    -H 'Content-Type: application/json' > $test_dir/test_result_poem.json

curl $connection/generate_stream \
    -X POST \
    -d "$prompt" \
    -H 'Content-Type: application/json' > $test_dir/test_result_poem.streamed.json


message="What is your name?"
prompt='{"inputs": "'${system_prompt}'### Human: '${message}'\\n\\n### Assistant:\\n","parameters":{"max_new_tokens":64}}'

curl $connection/generate \
    -X POST \
    -d "$prompt" \
    -H 'Content-Type: application/json' > $test_dir/test_result_name.json

curl $connection/generate_stream \
    -X POST \
    -d "$prompt" \
    -H 'Content-Type: application/json' > $test_dir/test_result_name.streamed.json


message="Who is Albert Einstein and what is his biggest contribution to science?"
prompt='{"inputs": "'${system_prompt}'### Human: '${message}'\\n\\n### Assistant:\\n","parameters":{"max_new_tokens":64}}'

curl $connection/generate \
    -X POST \
    -d "$prompt" \
    -H 'Content-Type: application/json' > $test_dir/test_result_einstein.json

curl $connection/generate_stream \
    -X POST \
    -d "$prompt" \
    -H 'Content-Type: application/json' > $test_dir/test_result_einstein.streamed.json
