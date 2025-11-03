#!/bin/bash

# options
showHelp=0
download=0
convert=0
upload=0
verbose=0

# parameters
downloadDataKey="asr_result_url"
localeKey="de"
uploadDataKey=""
torch_device="cpu"

while getopts hd:gl:u:v flag
do
    case "${flag}" in
        h) showHelp=1;;
        d) convert=1; download=1; downloadDataKey=$OPTARG;;
        g) torch_device="cuda";;
        l) localeKey=$OPTARG;;
        u) upload=1; uploadDataKey=$OPTARG;;
        v) verbose=1;;
    esac
done

function printHelp() {
    echo "Downloads and translates to target language (default 'de') TopicResult json or ShortSummaryResult json file and uploads it"
    echo "Usage:"
    echo "  normalize.sh -d <data-key> -l <locale> -u <data-key> [-v]"
    echo "Parameters: "
    echo "  -d: Download file from download url using data key contained in DOWNLOAD_DATA environment variable"
    echo "  -l: locale for translation, default: 'de', values: 'de', 'en'"
    echo "  -u: Upload converted file to upload url, parameter is the data key for the upload url"
    echo "  -v: Verbose output"
    echo "Example:"
    echo "  translate.sh -d topic_result_en_url -l de -u topic_result_de_upload_url"
    echo "  translate.sh -d short_summary_result_en_url -l de -u short_summary_result_de_upload_url"
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

    if [[ $convert -eq 1 ]]; then
        inputFile="proc_result.json"
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

        outputFile="proc_result.$localeKey.json"
        echo "Translating ${AIRFLOW_TMP_DIR}/$inputFile to ${AIRFLOW_TMP_DIR}/$outputFile"
        python3 translate.py -d "$torch_device" -i "${AIRFLOW_TMP_DIR}/$inputFile" -l "$localeKey" -o "${AIRFLOW_TMP_DIR}/$outputFile" & PID=$!
        echo "Translation is ongoing"
        while kill -0 $PID 2> /dev/null; do
            echo -n "."
            sleep 30
        done
        retVal=$?
        if [ $retVal -ne 0 ]; then
            echo "Error during nlp translation!"
            exit $retVal
        fi

        if [[ $upload -eq 1 ]]; then
            url_upload=$(python3 parse_xcom.py "${UPLOAD_DATA}" "$uploadDataKey")
            echo "Uploading $outputFile to ${url_upload}"
            curl -X PUT "$url_upload" --upload-file "${AIRFLOW_TMP_DIR}/$outputFile" -v
        fi

        echo '{"result": "finished"}'
    else
        printHelp
        exit 1
    fi
fi
