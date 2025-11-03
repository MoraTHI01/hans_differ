#!/bin/bash

# options
showHelp=0
download=0
recognize=0
upload=0
verbose=0
punctuation=0

# parameters
downloadDataKey="audio_raw_url"
localeKey="asr_locale"
mod9server=""
mod9port=""
uploadDataKey=""

# static
inputFile="temp.wav"
outputFile="asr_result_raw.json"
uploadFile="asr_result.json"

while getopts hd:l:p:s:u:vw flag
do
    case "${flag}" in
        h) showHelp=1;;
        d) download=1; downloadDataKey=$OPTARG;;
        l) localeKey=$OPTARG;;
        p) recognize=1; mod9port=$OPTARG;;
        s) recognize=1; mod9server=$OPTARG;;
        u) upload=1; uploadDataKey=$OPTARG;;
        v) verbose=1;;
        w) punctuation=1;;
    esac
done

function printHelp() {
    echo "Downloads and creates a transcript of a raw audio file using mod9 engine and uploads it"
    echo "Usage:"
    echo "  recognize.sh -d -s <server> -p <port> -u <data-key> [-v]"
    echo "Parameters: "
    echo "  -d: Download url data key contained in DOWNLOAD_DATA environment variable for resolving download url for raw audio"
    echo "  -l: locale data key contained in ASR_LOCALE environment variable for resolving asr locale"
    echo "  -p: Port of the mod9 engine"
    echo "  -s: Server url of the mod9 engine"
    echo "  -u: Upload transcript file to upload url, parameter is the data key for the upload url contained in UPLOAD_DATA environment variable"
    echo "  -v: Verbose output"
    echo "  -w: With capitalization, punctuation, number-formatting, etc. on mod9 engine"
    echo "Example:"
    echo "  recognize.sh -d audio_raw_url -l asr_locale -s localhost -p 9900 -u asr_result_url"
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
    echo "- MOD9_SERVER: $mod9server"
    echo "- MOD9_PORT: $mod9port"
    echo "- UPLOAD_DATA_KEY: $uploadDataKey"

    if [[ $recognize -eq 1 ]]; then

        if [[ $download -eq 1 ]]; then
          url_download=$(python3 parse_xcom.py "${DOWNLOAD_DATA}" "$downloadDataKey")
          echo "Downloading $inputFile from $url_download to ${AIRFLOW_TMP_DIR}/$inputFile"
          curl "${url_download}" --output "${AIRFLOW_TMP_DIR}/$inputFile"
        fi

        locale=$(python3 parse_xcom.py "${ASR_LOCALE}" "$localeKey")
        asrModel="${locale}_video"
        echo "- MOD9_ASR_MODEL: $asrModel"

        echo "Checking mod9 health status"
        info=$(echo '{"command":"get-info"}' | nc -w 1 $mod9server $mod9port)
        if [[ ! $info == *"state"*":"*"ready"* ]]; then
            echo "Error: Engine not ready!"
            exit 1
        else
            echo "Engine ready!"
        fi
        echo '{"command":"get-info"}' | nc $mod9server $mod9port > "${AIRFLOW_TMP_DIR}/asr_engine_info.json"
        echo '{"command":"get-models-info"}' | nc $mod9server $mod9port > "${AIRFLOW_TMP_DIR}/asr_model_info.json"

        echo "Transcribing ${AIRFLOW_TMP_DIR}/$inputFile to ${AIRFLOW_TMP_DIR}/$outputFile"
        if [[ $punctuation -eq 1 ]]; then
            (echo '{"command": "recognize", "batch-threads": -1, "word-intervals": true, "word-confidence": true, "transcript-formatted": true, "transcript-intervals": true, "word-alternatives-confidence": true, "word-alternatives": 3, "asr-model": "'"$asrModel"'" }'; cat "${AIRFLOW_TMP_DIR}/$inputFile") | nc $mod9server $mod9port > "${AIRFLOW_TMP_DIR}/$outputFile"
        else
            (echo '{"command": "recognize", "batch-threads": -1, "word-intervals": true, "word-confidence": true, "transcript-formatted": false, "transcript-intervals": true, "word-alternatives-confidence": true, "word-alternatives": 3, "asr-model": "'"$asrModel"'" }'; cat "${AIRFLOW_TMP_DIR}/$inputFile") | nc $mod9server $mod9port > "${AIRFLOW_TMP_DIR}/$outputFile"
        fi

        wordcount=$(wc -c ${AIRFLOW_TMP_DIR}/$outputFile | awk '{print $1}')
        if [ "$wordcount" -lt 45 ]
        then
            echo "Error: Invalid raw recognition result!"
            exit 1
        fi

        echo "Converting ${AIRFLOW_TMP_DIR}/$outputFile to ${AIRFLOW_TMP_DIR}/$uploadFile"
        python3 convert_to_asr_result.py "${AIRFLOW_TMP_DIR}/$outputFile" "${AIRFLOW_TMP_DIR}/asr_engine_info.json" "${AIRFLOW_TMP_DIR}/asr_model_info.json" "$asrModel" "${AIRFLOW_TMP_DIR}/$uploadFile"
        retVal=$?
        if [ $retVal -ne 0 ]; then
            echo "Error during conversion of asr result for HAnS!"
            exit $retVal
        fi

        wordcount=$(wc -c ${AIRFLOW_TMP_DIR}/$uploadFile | awk '{print $1}')
        if [ "$wordcount" -lt 45 ]
        then
            echo "Error: Invalid recognition result!"
            exit 1
        fi

        if [[ $upload -eq 1 ]]; then
          url_upload=$(python3 parse_xcom.py "${UPLOAD_DATA}" "$uploadDataKey")
          echo "Uploading $uploadFile to ${url_upload}"
          curl -X PUT "$url_upload" --upload-file "${AIRFLOW_TMP_DIR}/$uploadFile" -v
        fi
        echo '{"result": "finished"}'
    else
        printHelp
        exit 1
    fi
fi
