#!/bin/bash

# options
showHelp=0
download=0
convert=0
upload=0
verbose=0

# parameters
downloadDataKey="asr_result_url"
localeKey="asr_locale"
uploadDataKey=""

while getopts hd:l:u:v flag
do
    case "${flag}" in
        h) showHelp=1;;
        d) convert=1; download=1; downloadDataKey=$OPTARG;;
        l) localeKey=$OPTARG;;
        u) upload=1; uploadDataKey=$OPTARG;;
        v) verbose=1;;
    esac
done

function printHelp() {
    echo "Downloads and normalizes asr_result.json file and uploads it"
    echo "Usage:"
    echo "  normalize.sh -d <data-key> -l <data-key> -u <data-key> [-v]"
    echo "Parameters: "
    echo "  -d: Download file from download url using data key contained in DOWNLOAD_DATA environment variable"
    echo "  -l: locale data key contained in ASR_LOCALE environment variable for resolving asr locale"
    echo "  -u: Upload converted file to upload url, parameter is the data key for the upload url"
    echo "  -v: Verbose output"
    echo "Example:"
    echo "  normalize.sh -d asr_result_url -l asr_locale -u transcript_upload_url"
}

if [[ $showHelp -eq 1 ]]
then
    printHelp
    exit 1
else
    echo "- ENV_AIRFLOW_TMP_DIR: ${AIRFLOW_TMP_DIR}"
    echo "- ENV_DOWNLOAD_DATA: ${DOWNLOAD_DATA}"
    echo "- ENV_UPLOAD_DATA: ${UPLOAD_DATA}"
    echo "- ENV_ASR_LOCALE: ${ASR_LOCALE}"
    echo "- UPLOAD_DATA_KEY: $uploadDataKey"

    if [[ $convert -eq 1 ]]; then
        inputFile="asr_result.json"
        if [[ $download -eq 1 ]]; then
          url_download=$(python3 parse_xcom.py "${DOWNLOAD_DATA}" "$downloadDataKey")
          echo "Downloading $inputFile from $url_download to ${AIRFLOW_TMP_DIR}/$inputFile"
          curl "${url_download}" --output "${AIRFLOW_TMP_DIR}/$inputFile"
        fi

        echo "Check if "${AIRFLOW_TMP_DIR}/$inputFile" is valid json"
        python3 -m json.tool "${AIRFLOW_TMP_DIR}/$inputFile" > /dev/null 2>&1
        retVal=$?
        if [ $retVal -ne 0 ]; then
            echo "Error invalid json input file detected during nlp text normalization!"
            exit $retVal
        fi

        locale=$(python3 parse_xcom.py "${ASR_LOCALE}" "$localeKey")

        outputFile="asr_result_normalized.json"
        echo "Converting ${AIRFLOW_TMP_DIR}/$inputFile to ${AIRFLOW_TMP_DIR}/$outputFile"
        python3 nlp_normalize.py "${AIRFLOW_TMP_DIR}/$inputFile" "$locale" "${AIRFLOW_TMP_DIR}/$outputFile"
        retVal=$?
        if [ $retVal -ne 0 ]; then
            echo "Error during nlp text normalization!"
            exit $retVal
        fi

        if [[ $upload -eq 1 ]]; then
          url_upload=$(python3 parse_xcom.py "${UPLOAD_DATA}" "$uploadDataKey")
          echo "Uploading $outputFile to ${url_upload}"
          curl -H "X-Amz-Meta-Filename: $outputFile" -H 'Content-Type: application/json' -X PUT "$url_upload" --upload-file "${AIRFLOW_TMP_DIR}/$outputFile" -v
        fi

        echo '{"result": "finished"}'
    else
        printHelp
        exit 1
    fi
fi
