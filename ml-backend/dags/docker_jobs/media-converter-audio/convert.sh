#!/bin/bash

# options
showHelp=0
download=0
convert=0
upload=0
verbose=0

# parameters
downloadDataKey="video_url,podcast_url"
downloadFilenameDataKey="video_filename,podcast_filename"
uploadDataKey=""

while getopts hd:f:u:v flag
do
    case "${flag}" in
        h) showHelp=1;;
        d) convert=1; download=1; downloadDataKey=$OPTARG;;
        f) convert=1; downloadFilenameDataKey=$OPTARG;;
        u) upload=1; uploadDataKey=$OPTARG;;
        v) verbose=1;;
    esac
done

function printHelp() {
    echo "Downloads and converts a video file and uploads it"
    echo "Usage:"
    echo "  convert.sh -d <data-key> -f <data-key> -u <data-key> [-v]"
    echo "Parameters: "
    echo "  -d: Download file from download url using data key contained in DOWNLOAD_DATA environment variable"
    echo "  -f: Fetch data key for the filename from DOWNLOAD_DATA environment variable"
    echo "  -u: Upload converted file to upload url, parameter is the data key for the upload url"
    echo "  -v: Verbose output"
    echo "Example:"
    echo "  convert.sh -d video_url,podcast_url -f video_filename,podcast_filename -u audio_raw_url"
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
        inputFile=$(python3 parse_xcom.py "${DOWNLOAD_DATA}" "$downloadFilenameDataKey")

        if [[ $download -eq 1 ]]; then
          url_download=$(python3 parse_xcom.py "${DOWNLOAD_DATA}" "$downloadDataKey")
          echo "Downloading $inputFile from $url_download to ${AIRFLOW_TMP_DIR}/$inputFile"
          curl "${url_download}" --output "${AIRFLOW_TMP_DIR}/$inputFile"
        fi

        outputFile="${inputFile%.*}.wav"
        echo "Converting ${AIRFLOW_TMP_DIR}/$inputFile to ${AIRFLOW_TMP_DIR}/$outputFile"
        ffmpeg -i "${AIRFLOW_TMP_DIR}/$inputFile" -acodec pcm_s16le -ar 16000 -ac 1 "${AIRFLOW_TMP_DIR}/$outputFile"
        retVal=$?
        if [ $retVal -ne 0 ]; then
            echo "Error during video to audio conversion!"
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
