#!/bin/bash

# options
showHelp=0
download=0
convert=0
parse=0
upload=0
verbose=0

# parameters
downloadDataKey="video_url"
parseUrnDataKey="video_dash_urn"
resolution="hd"
# 0 = default = optimal = all, 1 (single-threaded), 2 (2 threads for e.g. an Intel Core 2 Duo);
ffmpeg_threads=0
singleResPreview=0

while getopts hd:p:r:st:uv flag
do
    case "${flag}" in
        h) showHelp=1;;
        d) convert=1; download=1; downloadDataKey=$OPTARG;;
        p) parse=1; parseUrnDataKey=$OPTARG;;
        r) resolution=$OPTARG;;
        s) singleResPreview=1;;
        t) ffmpeg_threads=$OPTARG;;
        u) upload=1;;
        v) verbose=1;;
    esac
done

function printHelp() {
    echo "Downloads and converts a video file and uploads it"
    echo "Usage:"
    echo "  convert.sh -d <data-key> -p <urn-data-key> -r <resolution> -u [-v]"
    echo "Parameters: "
    echo "  -d: Download file from download url using data key contained in DOWNLOAD_DATA environment variable"
    echo "  -p: Parse UUID of URN from URN_DATA environment variable, parameter is the data key for the urn"
    echo "  -r: Resolution, 'full-hd' or 'hd', default: 'hd'"
    echo "  -s: Single resolution preview mode"
    echo "  -t: ffmpeg threads, '0' for optimal threads, '1' for single thread, '2', ..., default: '0'"
    echo "  -u: Upload converted files using parsed UUID from URN_DATA"
    echo "  -v: Verbose output"
    echo "Example:"
    echo "  convert.sh -d video_url -p video_dash_urn -r hd -u"
}

if [[ $showHelp -eq 1 ]]
then
    printHelp
    exit 1
else
    echo "- ENV_AIRFLOW_TMP_DIR: ${AIRFLOW_TMP_DIR}"
    echo "- ENV_DOWNLOAD_DATA: ${DOWNLOAD_DATA}"
    echo "- ENV_URN_DATA: ${URN_DATA}"
    echo "- ENV_ASSETDB_TEMP_CONFIG: ${ASSETDB_TEMP_CONFIG}"
    echo "- PARSE_UUID_DATA_KEY: $parseUrnDataKey"
    echo "- RESOLUTION: $resolution"

    if [[ $convert -eq 1 ]]; then

        if [[ $parse -eq 1 ]]; then
            urn=$(python3 parse_xcom.py "${URN_DATA}" "$parseUrnDataKey")
            arrIN=(${urn//:/ })
            uuidWithFileExt=${arrIN[-1]}
            arrUUID=(${uuidWithFileExt//./ })
            uuid=${arrUUID[0]}
        fi
        echo "VIDEO_UUID: $uuid"
        inputFile="${uuid}.mp4"
        echo "VIDEO_INPUT_FILE: $inputFile"

        if [[ $download -eq 1 ]]; then
          url_download=$(python3 parse_xcom.py "${DOWNLOAD_DATA}" "$downloadDataKey")
          echo "Downloading $inputFile from $url_download to ${AIRFLOW_TMP_DIR}/$inputFile"
          curl "${url_download}" --output "${AIRFLOW_TMP_DIR}/$inputFile"
        fi

        outputFolder="${AIRFLOW_TMP_DIR}"
        echo "Converting ${AIRFLOW_TMP_DIR}/$inputFile to MPEG-DASH with max. $resolution resolution into folder $outputFolder"
        if [[ $verbose -eq 1 ]]; then
            if [[ $singleResPreview -eq 1 ]]; then
                ./create_dash.sh -i "${AIRFLOW_TMP_DIR}/$inputFile" -o "$outputFolder" -r "$resolution" -t $ffmpeg_threads -v -s
            else
                ./create_dash.sh -i "${AIRFLOW_TMP_DIR}/$inputFile" -o "$outputFolder" -r "$resolution" -t $ffmpeg_threads -v
            fi
        else
            if [[ $singleResPreview -eq 1 ]]; then
                ./create_dash.sh -i "${AIRFLOW_TMP_DIR}/$inputFile" -o "$outputFolder" -r "$resolution" -t $ffmpeg_threads -s
            else
                ./create_dash.sh -i "${AIRFLOW_TMP_DIR}/$inputFile" -o "$outputFolder" -r "$resolution" -t $ffmpeg_threads
            fi
        fi
        retVal=$?
        if [ $retVal -ne 0 ]; then
            echo "Error during mpeg-dash conversion!"
            exit $retVal
        fi
        echo ""

        if [[ $upload -eq 1 ]]; then
          prev_dir=$(pwd)
          cd "$outputFolder"
          for tempfile in $(pwd)/* ; do
              tempfilename="${tempfile##*/}"
              # All files should start with the uuid
              if [[ "$tempfilename" == $uuid* ]]; then
                    # Don't upload original mp4
                    if [[ ! "$tempfilename" == *mp4 ]]; then
                        echo "Uploading $tempfile to ${urn}/$tempfilename"
                        python3 $prev_dir/upload_assetdb_temp.py "$ASSETDB_TEMP_CONFIG" "${urn}" "$tempfilename"
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
