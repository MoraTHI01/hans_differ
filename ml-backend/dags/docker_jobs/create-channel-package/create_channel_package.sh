#!/bin/bash

# options
showHelp=0
package=0
verbose=0
# parameters
packageUuid=""

while getopts hp:v flag
do
    case "${flag}" in
        h) showHelp=1;;
        p) package=1; packageUuid=$OPTARG;;
        v) verbose=1;;
    esac
done

function printHelp() {
    echo "Create a channel package"
    echo "Usage:"
    echo "  create_channel.sh [-v]"
    echo "Parameters: "
    echo "  -v: Verbose output"
    echo "Example:"
    echo "  create_channel.sh"
}

if [[ $showHelp -eq 1 ]]
then
    printHelp
    exit 1
else
    echo "- ENV_AIRFLOW_TMP_DIR: ${AIRFLOW_TMP_DIR}"
    echo "- ENV_UPLOAD_URL: ${UPLOAD_URL}"
    echo "- ENV_CHANNEL_DATA: ${CHANNEL_DATA}"
    echo "- ENV_ASSETDB_TEMP_CONFIG: ${ASSETDB_TEMP_CONFIG}"

    if [[ $package -eq 1 ]]; then
        echo "- Storing download files to ${AIRFLOW_TMP_DIR}/channel-package-$packageUuid"
        packages_folder=${AIRFLOW_TMP_DIR}/channel-package-$packageUuid
        python3 download_assetdb_temp.py "$ASSETDB_TEMP_CONFIG" "${packages_folder}" "archive-bucket" "*"
        retVal=$?
        if [ $retVal -ne 0 ]; then
            echo "Error during channel package downloading of package files for HAnS!"
            exit $retVal
        fi
        echo "- Storing channel.json to ${packages_folder}/channel.json"
        echo "${CHANNEL_DATA}" > "${packages_folder}/channel_temp.json"
        retVal=$?
        if [ $retVal -ne 0 ]; then
            echo "Error during channel package creation channel.json for HAnS!"
            exit $retVal
        fi
        #sed "s/'/"\""/g" "${packages_folder}/channel_temp.json" > "${packages_folder}/channel.json"
        sed "s/'/\"/g" "${packages_folder}/channel_temp.json" > "${packages_folder}/channel.json"
        retVal=$?
        if [ $retVal -ne 0 ]; then
            echo "Error during channel package creation channel.json fix quotes for HAnS!"
            exit $retVal
        fi
        rm "${packages_folder}/channel_temp.json"
        echo ""
        echo "Channel.json:"
        cat "${packages_folder}/channel.json"
        echo ""
        echo "Channel package content:"
        ls -lisa "${packages_folder}/"
        echo ""
        channel_package_path=${AIRFLOW_TMP_DIR}/$packageUuid.tar.gz
        echo "Creating package archive $channel_package_path"
        work_dir=$(pwd)
        cd $packages_folder
        tar -czvf $channel_package_path .
        echo "Created package archive $channel_package_path"
        # This was commented before, disabling the upload of the package to the packages - no documentation was provided of why this was executed
        cd $work_dir
        url_upload=$(python3 parse_xcom.py "${UPLOAD_URL}" "result")
        echo "Uploading $channel_package_path to $url_upload"
        curl -X PUT "$url_upload" --upload-file "$channel_package_path" --compressed --max-time 7200 --connect-timeout 30 -v
        # This was commented before, disabling the upload of the package to the packages - no documentation was provided of why this was executed
        echo '{"result": "finished"}'
    else
        printHelp
        exit 1
    fi
fi
