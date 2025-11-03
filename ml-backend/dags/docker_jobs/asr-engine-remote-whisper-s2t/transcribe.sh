#!/bin/bash

# options
showHelp=0
verbose=0

# parameters
asrModel="large-v3"
batchSize=8
connection="127.0.0.1:8099"
inputFile="temp.wav"
outputFile="result.json"
language="de"
task="transcribe"

while getopts hb:c:i:o:l:m:t:v flag
do
    case "${flag}" in
        h) showHelp=1;;
        b) batchSize=$OPTARG;;
        c) connection=$OPTARG;;
        i) inputFile=$OPTARG;;
        o) outputFile=$OPTARG;;
        l) language=$OPTARG;;
        m) asrModel=$OPTARG;;
        t) task=$OPTARG;;
        v) verbose=1;;
    esac
done

function printHelp() {
    echo "Creates transcript of a raw audio file using remote engine"
    echo "Usage:"
    echo "  recognize.sh -p <port> -r <server-url> -b <batch-size> -l <language> [-m <model-name>] [-v]"
    echo "Parameters: "
    echo "  -c: Remote server and port connection url of the whisper-s2t engine"
    echo "  -b: Batch size to use, e.g. 8, 16 or 48"
    echo "  -m: Whisper ASR model, default: large-v3"
    echo "  -l: Language id 'en', 'de'"
    echo "  -t: Task 'transcribe' or 'translate'"
    echo "  -v: Verbose output"
    echo "Example:"
    echo "  transcribe.sh -c 127.0.0.1:8099 -b 8 -l de -i input.wav -o result.json"
}

if [[ $showHelp -eq 1 ]]
then
    printHelp
    exit 1
else
    echo "- task: ${task}"
    echo "- model: ${asrModel}"
    echo "- language: ${language}"
    echo "- batch_size: ${batchSize}"
    echo "- inputFile: ${inputFile}"
    echo "- outputFile: ${outputFile}"

    echo "Generating request"
    echo '{"file": "'$(base64 < "$inputFile" | tr -d '\n')'",
       "model": "'"$asrModel"'",
       "language": "'"$language"'",
       "batch_size": "'"$batchSize"'",
       "sample_rate": 16000}' > temp.json

    echo "Sending request to $connection/$task"
    while true; do
        status=$(curl -s "$connection/info" -H 'Content-Type: application/json' | jq -r '.result.status')
        if [ "$status" = "BUSY" ]; then
            echo "Status is still BUSY. Waiting..."
            sleep 5  # Adjust the sleep duration as needed
        else
            echo "Status is not BUSY anymore. It might be running."
            break
        fi
    done
    curl "$connection/$task" -H 'Content-Type: application/json' --data-binary @temp.json -o "$outputFile"
fi
