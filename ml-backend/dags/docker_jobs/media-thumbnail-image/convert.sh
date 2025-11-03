#!/bin/bash

# options
showHelp=0
download=0
convert=0
upload=0
verbose=0

# parameters
downloadDataKey="video_url"
downloadFilenameDataKey="video_filename"
uploadDataKey="video_thumb_urn"
resolution="hd"

while getopts hd:f:r:u:v flag
do
    case "${flag}" in
        h) showHelp=1;;
        d) convert=1; download=1; downloadDataKey=$OPTARG;;
        f) convert=1; downloadFilenameDataKey=$OPTARG;;
        r) resolution=$OPTARG;;
        u) upload=1; uploadDataKey=$OPTARG;;
        v) verbose=1;;
    esac
done

function printHelp() {
    echo "Downloads and creates a thumbnail of a video file and uploads it"
    echo "Usage:"
    echo "  convert.sh -d <data-key> -f <data-key> -r <resolution> -u <data-key> [-v]"
    echo "Parameters: "
    echo "  -d: Download file from download url using data key contained in DOWNLOAD_DATA environment variable"
    echo "  -f: Fetch data key for the filename from DOWNLOAD_DATA environment variable"
    echo "  -r: Resolution, 'full-hd' or 'hd', default: 'hd'"
    echo "  -u: Upload converted files using UUID from UPLOAD_DATA, parameter is the data key for the url"
    echo "  -v: Verbose output"
    echo "Example:"
    echo "  convert.sh -d video_url -f video_filename -r hd -u video_thumb"
}

if [[ $showHelp -eq 1 ]]
then
    printHelp
    exit 1
else
    echo "- ENV_AIRFLOW_TMP_DIR: ${AIRFLOW_TMP_DIR}"
    echo "- ENV_DOWNLOAD_DATA: ${DOWNLOAD_DATA}"
    echo "- ENV_UPLOAD_DATA: ${UPLOAD_DATA}"
    echo "- ENV_ASSETDB_TEMP_CONFIG: ${ASSETDB_TEMP_CONFIG}"
    echo "- UPLOAD_DATA_KEY: $uploadDataKey"
    echo "- RESOLUTION: $resolution"

    if [[ $convert -eq 1 ]]; then
        inputFile=$(python3 parse_xcom.py "${DOWNLOAD_DATA}" "$downloadFilenameDataKey")
        filePrefix="${inputFile%.*}"

        if [[ $download -eq 1 ]]; then
            url_download=$(python3 parse_xcom.py "${DOWNLOAD_DATA}" "$downloadDataKey")
            echo "Downloading $inputFile from $url_download to ${AIRFLOW_TMP_DIR}/$inputFile"
            curl "${url_download}" --output "${AIRFLOW_TMP_DIR}/$inputFile"
            uuid=$(echo "$url_download" | grep -oP '(?<=/)[a-f0-9\-]{36}(?=\.mp4)')
            filePrefix="${uuid%.*}"
        fi

        echo "Creating thumbnail images from ${AIRFLOW_TMP_DIR}/$inputFile to ${AIRFLOW_TMP_DIR}/$filePrefix-tn-w320-h180-%04d.png"
        ffmpeg -i "${AIRFLOW_TMP_DIR}/$inputFile" -vf "thumbnail=2,fps=1/10,scale=320:180:flags=lanczos" -aspect "16:9" -vsync cfr -r 1/10 "${AIRFLOW_TMP_DIR}/$filePrefix-tn-w320-h180-%04d.png"
        retVal=$?
        if [ $retVal -ne 0 ]; then
            echo "Error during thumbnail images extraction in w320!"
            exit $retVal
        fi
        python3 convert_images.py --input-folder "${AIRFLOW_TMP_DIR}/"
        retVal=$?
        if [ $retVal -ne 0 ]; then
            echo "Error during thumbnail images conversion!"
            exit $retVal
        fi
        python3 thumbnails_count_to_timestamp.py --input-folder "${AIRFLOW_TMP_DIR}/"
        retVal=$?
        if [ $retVal -ne 0 ]; then
            echo "Error during thumbnail images renaming!"
            exit $retVal
        fi

        outputFile="$filePrefix.thumb.png"
        params="scale=1280x720:force_original_aspect_ratio=decrease,pad=1280:720:-1:-1:color=black"
        if [[ $resolution == "hd" ]]; then
            params="scale=1280x720:force_original_aspect_ratio=decrease,pad=1280:720:-1:-1:color=black"
        elif [[ $resolution == "full-hd" ]]; then
            params="scale=1920x1080:force_original_aspect_ratio=decrease,pad=1920:1080:-1:-1:color=black"
        fi
        echo "Creating thumbnail image of ${AIRFLOW_TMP_DIR}/$inputFile to ${AIRFLOW_TMP_DIR}/$outputFile"
        ffmpeg -i "${AIRFLOW_TMP_DIR}/$inputFile" -ss 00:00:07 -frames:v 1 -vf $params -aspect "16:9" "${AIRFLOW_TMP_DIR}/$outputFile"
        retVal=$?
        if [ $retVal -ne 0 ]; then
            echo "Error during video to thumbnail image conversion!"
            exit $retVal
        fi

        if [[ $upload -eq 1 ]]; then
            url_upload=$(python3 parse_xcom.py "${UPLOAD_DATA}" "$uploadDataKey")
            prev_dir=$(pwd)
            cd "${AIRFLOW_TMP_DIR}/"
            for tempfile in $(pwd)/* ; do
                tempfilename="${tempfile##*/}"
                # All files should start with the uuid
                if [[ "$tempfilename" == $filePrefix* ]]; then
                      # Don't upload original mp4
                      if [[ ! "$tempfilename" == *mp4 ]]; then
                          echo "Uploading $tempfile to ${url_upload}/$tempfilename"
                          python3 $prev_dir/upload_assetdb_temp.py "$ASSETDB_TEMP_CONFIG" "${url_upload}" "$tempfilename"
                      fi
                fi
                echo ""
            done
            cd "$prev_dir"
        fi

        echo '{"result": "finished"}'
    else
        printHelp
        exit 1
    fi
fi
