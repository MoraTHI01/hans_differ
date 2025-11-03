#!/bin/bash

# options
showHelp=0
download=0
upload=0
verbose=0

# parameters
embedding_model=""
downloadDataKey="subtitle_en_url"
uploadDataKey=""
torch_device="cpu"

while getopts hd:m:g:u:v flag
do
    case "${flag}" in
        h) showHelp=1;;
        d) download=1; downloadDataKey=$OPTARG;;
        m) embedding_model=$OPTARG;;
        g) torch_device="cuda";;
        u) upload=1; uploadDataKey=$OPTARG;;
        v) verbose=1;;
    esac
done

function printHelp() {
    echo "Downloads VTT Transcript of lecture, performs topic segmentation and uploads the TopicResultRaw file"
    echo "Usage:"
    echo "  segment.sh -d <data-key> -u <data-key> [-v]"
    echo "Parameters: "
    echo "  -m: Embedding model to be used, one from https://huggingface.co/sentence-transformers"
    echo "  -d: Download file from download url using data key contained in DOWNLOAD_DATA environment variable"
    echo "  -u: Upload converted file to upload url, parameter is the data key for the upload url"
    echo "  -v: Verbose output"
    echo "Example:"
    echo "  segment.sh -m sentence-transformers/paraphrase-multilingual-mpnet-base-v2 -d vtt_transcript_url -u topic_result_upload_url"
}

if [[ $showHelp -eq 1 ]]
then
    printHelp
    exit 1
else
    echo "- ENV_AIRFLOW_TMP_DIR: ${AIRFLOW_TMP_DIR}"
    echo "- ENV_DOWNLOAD_DATA: ${DOWNLOAD_DATA}"
    echo "- ENV_UPLOAD_DATA: ${UPLOAD_DATA}"
    echo "- UPLOAD_DATA_KEY: $uploadDataKey"
    echo "- Download data key: $downloadDataKey"

    inputFile="proc_result.vtt"
    if [[ $download -eq 1 ]]; then
      url_download=$(python3 parse_xcom.py "${DOWNLOAD_DATA}" "$downloadDataKey")
      echo "Downloading $inputFile from $url_download to ${AIRFLOW_TMP_DIR}/$inputFile"
      curl "${url_download}" --output "${AIRFLOW_TMP_DIR}/$inputFile"
    fi

    outputFile="topic_result.json"
    echo "Segmenting ${AIRFLOW_TMP_DIR}/$inputFile to ${AIRFLOW_TMP_DIR}/$outputFile"
    python3 segment.py -i "${AIRFLOW_TMP_DIR}/$inputFile" -o "${AIRFLOW_TMP_DIR}/$outputFile" \
        -m "$embedding_model" -d "$torch_device" & PID=$!

    echo "Topic Segmentation is ongoing"
    while kill -0 $PID 2> /dev/null; do
        echo -n "."
        sleep 30
    done
    retVal=$?
    if [ $retVal -ne 0 ]; then
        echo "Error during Topic Segmentation!"
        exit $retVal
    fi

    if [[ $upload -eq 1 ]]; then
        url_upload=$(python3 parse_xcom.py "${UPLOAD_DATA}" "$uploadDataKey")
        echo "Uploading $outputFile to ${url_upload}"
        curl -X PUT "$url_upload" --upload-file "${AIRFLOW_TMP_DIR}/$outputFile" -v
    fi

    echo '{"result": "finished"}'
fi
