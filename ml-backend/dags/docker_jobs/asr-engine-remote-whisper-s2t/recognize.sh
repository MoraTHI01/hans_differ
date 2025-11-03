#!/bin/bash

# options
showHelp=0
download=0
recognize=1
upload=0
verbose=0

# parameters
downloadDataKey="audio_raw_url"
localeKey="asr_locale"
uploadDataKeyAsrResult_DE=""
uploadDataKeyTranscript_DE=""
uploadDataKeySubtitle_DE=""
uploadDataKeyAsrResult_EN=""
uploadDataKeyTranscript_EN=""
uploadDataKeySubtitle_EN=""
asrModel="large-v3"
batch_size=8
connection="127.0.0.1:8099"

# static
inputFile="temp.wav"
# temp files
asrResultFile="asr_result.json"
transcriptFile="asr_result_normalized.json"
subtitleFile="subtitle.vtt"
# language dep files
asrResultFile_DE="asr_result_de.json"
transcriptFile_DE="asr_result_de_normalized.json"
subtitleFile_DE="subtitle_de.vtt"
asrResultFile_EN="asr_result_en.json"
transcriptFile_EN="asr_result_en_normalized.json"
subtitleFile_EN="subtitle_en.vtt"

while getopts hb:c:d:l:m:s:t:u:x:y:z:v flag
do
    case "${flag}" in
        h) showHelp=1;;
        b) batch_size=$OPTARG;;
        c) connection=$OPTARG;;
        d) download=1; downloadDataKey=$OPTARG;;
        l) localeKey=$OPTARG;;
        m) asrModel=$OPTARG;;
        s) upload=1; uploadDataKeySubtitle_DE=$OPTARG;;
        t) upload=1; uploadDataKeyTranscript_DE=$OPTARG;;
        u) upload=1; uploadDataKeyAsrResult_DE=$OPTARG;;
        x) upload=1; uploadDataKeyAsrResult_EN=$OPTARG;;
        y) upload=1; uploadDataKeyTranscript_EN=$OPTARG;;
        z) upload=1; uploadDataKeySubtitle_EN=$OPTARG;;
        v) verbose=1;;
    esac
done

function printHelp() {
    echo "Downloads and creates a transcript of a raw audio file using whisper and uploads it"
    echo "Usage:"
    echo "  recognize.sh -p <port> -r <server-url> -b <batch-size> -d <data-key> -l <data-key> -u <data-key> -t <data-key> -s <data-key> [-c <number>] [-m <model-name>] [-g] [-v]"
    echo "Parameters: "
    echo "  -c: Remote server and port connection url of the whisper-s2t engine"
    echo "  -b: Batch size to use"
    echo "  -m: Whisper ASR model, default: large-v3"
    echo "  -l: locale data key contained in ASR_LOCALE environment variable for resolving asr locale"
    echo "  -d: Download url data key contained in DOWNLOAD_DATA environment variable for resolving download url for raw audio"
    echo "  -u: Upload asr result de file to upload url, parameter is the data key for the upload url contained in UPLOAD_DATA_KEY_ASR_RESULT_DE environment variable"
    echo "  -t: Upload transcript de file to upload url, parameter is the data key for the upload url contained in UPLOAD_DATA_KEY_TRANSCRIPT_DE environment variable"
    echo "  -s: Upload subtitle vtt de file to upload url, parameter is the data key for the upload url contained in UPLOAD_DATA_KEY_SUBTITLE_DE environment variable"
    echo "  -x: Upload asr result en file to upload url, parameter is the data key for the upload url contained in UPLOAD_DATA_KEY_ASR_RESULT_EN environment variable"
    echo "  -y: Upload transcript en file to upload url, parameter is the data key for the upload url contained in UPLOAD_DATA_KEY_TRANSCRIPT_EN environment variable"
    echo "  -z: Upload subtitle vtt en file to upload url, parameter is the data key for the upload url contained in UPLOAD_DATA_KEY_SUBTITLE_EN environment variable"
    echo "  -v: Verbose output"
    echo "Example:"
    echo "  recognize.sh -p 8099 -r 127.0.0.1 -b 8 -d audio_raw_url -l asr_locale -u asr_result_de_url -t transcript_de_url -s subtitle_de_url -x asr_result_en_url -y transcript_en_url -z subtitle_en_url"
}

if [[ $showHelp -eq 1 ]]
then
    printHelp
    exit 1
else
    echo "- ENV_AIRFLOW_TMP_DIR: ${AIRFLOW_TMP_DIR}"
    echo "- ENV_DOWNLOAD_DATA: ${DOWNLOAD_DATA}"
    echo "- ENV_UPLOAD_DATA_ASR_RESULT_DE: ${UPLOAD_DATA_ASR_RESULT_DE}"
    echo "- ENV_UPLOAD_DATA_TRANSCRIPT_DE: ${UPLOAD_DATA_TRANSCRIPT_DE}"
    echo "- ENV_UPLOAD_DATA_SUBTITLE_DE: ${UPLOAD_DATA_SUBTITLE_DE}"
    echo "- ENV_UPLOAD_DATA_ASR_RESULT_EN: ${UPLOAD_DATA_ASR_RESULT_EN}"
    echo "- ENV_UPLOAD_DATA_TRANSCRIPT_EN: ${UPLOAD_DATA_TRANSCRIPT_EN}"
    echo "- ENV_UPLOAD_DATA_SUBTITLE_EN: ${UPLOAD_DATA_SUBTITLE_EN}"
    echo "- ENV_ASR_LOCALE: ${ASR_LOCALE}"
    echo "- UPLOAD_DATA_KEY_ASR_RESULT_DE: $uploadDataKeyAsrResult_DE"
    echo "- UPLOAD_DATA_KEY_TRANSCRIPT_DE: $uploadDataKeyTranscript_DE"
    echo "- UPLOAD_DATA_KEY_SUBTITLE_DE: $uploadDataKeySubtitle_DE"
    echo "- UPLOAD_DATA_KEY_ASR_RESULT_EN: $uploadDataKeyAsrResult_EN"
    echo "- UPLOAD_DATA_KEY_TRANSCRIPT_EN: $uploadDataKeyTranscript_EN"
    echo "- UPLOAD_DATA_KEY_SUBTITLE_EN: $uploadDataKeySubtitle_EN"
    echo "- ENGINE_SERVER_URL: $connection"

    if [[ $recognize -eq 1 ]]; then

        if [[ $download -eq 1 ]]; then
          url_download=$(python3 parse_xcom.py "${DOWNLOAD_DATA}" "$downloadDataKey")
          echo "Downloading $inputFile from $url_download to ${AIRFLOW_TMP_DIR}/$inputFile"
          curl "${url_download}" --output "${AIRFLOW_TMP_DIR}/$inputFile"
        fi

        language=$(python3 parse_xcom.py "${ASR_LOCALE}" "$localeKey")

        verboseValue="False"
        if [[ $verbose -eq 1 ]]
        then
            verboseValue="True"
        fi
        echo "- WHISPER_ASR_MODEL: $asrModel"

        audiofilename=$(basename $inputFile)
        outputFile="${audiofilename%.*}.json"
        outputFile_DE="${audiofilename%.*}_de.json"
        outputFile_EN="${audiofilename%.*}_en.json"

        if [ "$language" == "en" ]; then
            echo "Transcribing ${AIRFLOW_TMP_DIR}/$inputFile to $outputFile_EN"
            ./transcribe.sh -c "$connection" -m "$asrModel" -l "$language" -t "transcribe" -b $batch_size -i "${AIRFLOW_TMP_DIR}/$inputFile" -o "${AIRFLOW_TMP_DIR}/$outputFile" & PID=$!
            echo "Transcription with whisper ongoing"
            while kill -0 $PID 2> /dev/null; do
                echo -n "."
                sleep 30
            done
            mv "${AIRFLOW_TMP_DIR}/$outputFile" "${AIRFLOW_TMP_DIR}/$outputFile_EN"
            echo ""
            echo "Transcription finished!"

            if [ ! -f "${AIRFLOW_TMP_DIR}/$outputFile_EN" ]; then
                echo "Error: File $outputFile_EN does not exist!"
                exit 1
            fi

            echo "Converting ${AIRFLOW_TMP_DIR}/$outputFile_EN to ${AIRFLOW_TMP_DIR}/$asrResultFile_EN"
            python3 convert_result_to_asr_result.py --input-file "${AIRFLOW_TMP_DIR}/$outputFile_EN" --output-file "${AIRFLOW_TMP_DIR}/$asrResultFile_EN"
            retVal=$?
            if [ $retVal -ne 0 ]; then
                echo "Error during conversion of asr result for HAnS!"
                exit $retVal
            fi
            wordcount=$(wc -c ${AIRFLOW_TMP_DIR}/$asrResultFile_EN | awk '{print $1}')
            if [ "$wordcount" -lt 45 ]
            then
                echo "Error: Invalid recognition result!"
                exit 1
            fi

            echo "Converting ${AIRFLOW_TMP_DIR}/$outputFile_EN to ${AIRFLOW_TMP_DIR}/$transcriptFile_EN"
            python3 convert_result_to_asr_normalized_result.py --input-file "${AIRFLOW_TMP_DIR}/$outputFile_EN" --output-file "${AIRFLOW_TMP_DIR}/$transcriptFile_EN"
            retVal=$?
            if [ $retVal -ne 0 ]; then
                echo "Error during conversion of transcript for HAnS!"
                exit $retVal
            fi
            wordcount=$(wc -c ${AIRFLOW_TMP_DIR}/$transcriptFile_EN | awk '{print $1}')
            if [ "$wordcount" -lt 45 ]
            then
                echo "Error: Invalid transcript!"
                exit 1
            fi

            echo "Converting ${AIRFLOW_TMP_DIR}/$transcriptFile_EN to ${AIRFLOW_TMP_DIR}/$subtitleFile_EN"
            python3 convert_asr_normalized_result_to_webvtt.py --input-file "${AIRFLOW_TMP_DIR}/$transcriptFile_EN" --output-file "${AIRFLOW_TMP_DIR}/$subtitleFile_EN"
            retVal=$?
            if [ $retVal -ne 0 ]; then
                echo "Error during conversion of subtitle for HAnS!"
                exit $retVal
            fi
            wordcount=$(wc -c ${AIRFLOW_TMP_DIR}/$subtitleFile_EN | awk '{print $1}')
            if [ "$wordcount" -lt 7 ]
            then
                echo "Error: Invalid webvtt file!"
                exit 1
            fi

            # Translate to German

            echo "Translating ${AIRFLOW_TMP_DIR}/$inputFile to ${AIRFLOW_TMP_DIR}/$outputFile_DE"
            ./transcribe.sh -c "$connection" -m "$asrModel" -l "de" -t "transcribe" -b $batch_size -i "${AIRFLOW_TMP_DIR}/$inputFile" -o "${AIRFLOW_TMP_DIR}/$outputFile" & PID=$!
            echo "Transcription with whisper ongoing"
            while kill -0 $PID 2> /dev/null; do
                echo -n "."
                sleep 30
            done
            mv "${AIRFLOW_TMP_DIR}/$outputFile" "${AIRFLOW_TMP_DIR}/$outputFile_DE"
            echo ""
            echo "Transcription finished!"

            if [ ! -f "${AIRFLOW_TMP_DIR}/$outputFile_DE" ]; then
                echo "Error: File ${AIRFLOW_TMP_DIR}/$outputFile_DE does not exist!"
                exit 1
            fi

            echo "Converting ${AIRFLOW_TMP_DIR}/$outputFile_DE to ${AIRFLOW_TMP_DIR}/$asrResultFile_DE"
            python3 convert_result_to_asr_result.py --input-file "${AIRFLOW_TMP_DIR}/$outputFile_DE" --output-file "${AIRFLOW_TMP_DIR}/$asrResultFile_DE"
            retVal=$?
            if [ $retVal -ne 0 ]; then
                echo "Error during conversion of asr result for HAnS!"
                exit $retVal
            fi
            wordcount=$(wc -c ${AIRFLOW_TMP_DIR}/$asrResultFile_DE | awk '{print $1}')
            if [ "$wordcount" -lt 45 ]
            then
                echo "Error: Invalid recognition result!"
                exit 1
            fi

            echo "Converting ${AIRFLOW_TMP_DIR}/$outputFile_DE to ${AIRFLOW_TMP_DIR}/$transcriptFile_DE"
            python3 convert_result_to_asr_normalized_result.py --input-file "${AIRFLOW_TMP_DIR}/$outputFile_DE" --output-file "${AIRFLOW_TMP_DIR}/$transcriptFile_DE"
            retVal=$?
            if [ $retVal -ne 0 ]; then
                echo "Error during conversion of transcript for HAnS!"
                exit $retVal
            fi
            wordcount=$(wc -c ${AIRFLOW_TMP_DIR}/$transcriptFile_DE | awk '{print $1}')
            if [ "$wordcount" -lt 45 ]
            then
                echo "Error: Invalid transcript!"
                exit 1
            fi

            echo "Converting ${AIRFLOW_TMP_DIR}/$transcriptFile_DE to ${AIRFLOW_TMP_DIR}/$subtitleFile_DE"
            python3 convert_asr_normalized_result_to_webvtt.py --input-file "${AIRFLOW_TMP_DIR}/$transcriptFile_DE" --output-file "${AIRFLOW_TMP_DIR}/$subtitleFile_DE"
            retVal=$?
            if [ $retVal -ne 0 ]; then
                echo "Error during conversion of transcript for HAnS!"
                exit $retVal
            fi
            wordcount=$(wc -c ${AIRFLOW_TMP_DIR}/$subtitleFile_DE | awk '{print $1}')
            if [ "$wordcount" -lt 7 ]
            then
                echo "Error: Invalid webvtt file!"
                exit 1
            fi

        elif [ "$language" == "de" ]; then
            echo "Transcribing ${AIRFLOW_TMP_DIR}/$inputFile to ${AIRFLOW_TMP_DIR}/$outputFile_DE"
            ./transcribe.sh -c "$connection" -m "$asrModel" -l "$language" -t "transcribe" -b $batch_size -i "${AIRFLOW_TMP_DIR}/$inputFile" -o "${AIRFLOW_TMP_DIR}/$outputFile" & PID=$!
            echo "Transcription with whisper ongoing"
            while kill -0 $PID 2> /dev/null; do
                echo -n "."
                sleep 30
            done
            mv "${AIRFLOW_TMP_DIR}/$outputFile" "${AIRFLOW_TMP_DIR}/$outputFile_DE"
            echo ""
            echo "Transcription finished!"

            if [ ! -f "${AIRFLOW_TMP_DIR}/$outputFile_DE" ]; then
                echo "Error: File ${AIRFLOW_TMP_DIR}/$outputFile_DE does not exist!"
                exit 1
            fi

            echo "Converting ${AIRFLOW_TMP_DIR}/$outputFile_DE to ${AIRFLOW_TMP_DIR}/$asrResultFile_DE"
            python3 convert_result_to_asr_result.py --input-file "${AIRFLOW_TMP_DIR}/$outputFile_DE" --output-file "${AIRFLOW_TMP_DIR}/$asrResultFile_DE"
            retVal=$?
            if [ $retVal -ne 0 ]; then
                echo "Error during conversion of asr result for HAnS!"
                exit $retVal
            fi
            wordcount=$(wc -c ${AIRFLOW_TMP_DIR}/$asrResultFile_DE | awk '{print $1}')
            if [ "$wordcount" -lt 45 ]
            then
                echo "Error: Invalid recognition result!"
                exit 1
            fi

            echo "Converting ${AIRFLOW_TMP_DIR}/$outputFile_DE to ${AIRFLOW_TMP_DIR}/$transcriptFile_DE"
            python3 convert_result_to_asr_normalized_result.py --input-file "${AIRFLOW_TMP_DIR}/$outputFile_DE" --output-file "${AIRFLOW_TMP_DIR}/$transcriptFile_DE"
            retVal=$?
            if [ $retVal -ne 0 ]; then
                echo "Error during conversion of transcript for HAnS!"
                exit $retVal
            fi
            wordcount=$(wc -c ${AIRFLOW_TMP_DIR}/$transcriptFile_DE | awk '{print $1}')
            if [ "$wordcount" -lt 45 ]
            then
                echo "Error: Invalid transcript!"
                exit 1
            fi

            echo "Converting ${AIRFLOW_TMP_DIR}/$transcriptFile_DE to ${AIRFLOW_TMP_DIR}/$subtitleFile_DE"
            python3 convert_asr_normalized_result_to_webvtt.py --input-file "${AIRFLOW_TMP_DIR}/$transcriptFile_DE" --output-file "${AIRFLOW_TMP_DIR}/$subtitleFile_DE"
            retVal=$?
            if [ $retVal -ne 0 ]; then
                echo "Error during conversion of transcript for HAnS!"
                exit $retVal
            fi
            wordcount=$(wc -c ${AIRFLOW_TMP_DIR}/$subtitleFile_DE | awk '{print $1}')
            if [ "$wordcount" -lt 7 ]
            then
                echo "Error: Invalid webvtt file!"
                exit 1
            fi

            # Translate to english

            echo "Transcribing ${AIRFLOW_TMP_DIR}/$inputFile to ${AIRFLOW_TMP_DIR}/$outputFile_EN"
            ./transcribe.sh -c "$connection" -m "$asrModel" -l "en" -t "translate" -b $batch_size -i "${AIRFLOW_TMP_DIR}/$inputFile" -o "${AIRFLOW_TMP_DIR}/$outputFile" & PID=$!
            echo "Transcription with whisper ongoing"
            while kill -0 $PID 2> /dev/null; do
                echo -n "."
                sleep 30
            done
            mv "${AIRFLOW_TMP_DIR}/$outputFile" "${AIRFLOW_TMP_DIR}/$outputFile_EN"
            echo ""
            echo "Transcription finished!"

            if [ ! -f "${AIRFLOW_TMP_DIR}/$outputFile_EN" ]; then
                echo "Error: File ${AIRFLOW_TMP_DIR}/$outputFile_EN does not exist!"
                exit 1
            fi

            echo "Converting ${AIRFLOW_TMP_DIR}/$outputFile_EN to ${AIRFLOW_TMP_DIR}/$asrResultFile_EN"
            python3 convert_result_to_asr_result.py --input-file "${AIRFLOW_TMP_DIR}/$outputFile_EN" --output-file "${AIRFLOW_TMP_DIR}/$asrResultFile_EN"
            retVal=$?
            if [ $retVal -ne 0 ]; then
                echo "Error during conversion of asr result for HAnS!"
                exit $retVal
            fi
            wordcount=$(wc -c ${AIRFLOW_TMP_DIR}/$asrResultFile_EN | awk '{print $1}')
            if [ "$wordcount" -lt 45 ]
            then
                echo "Error: Invalid recognition result!"
                exit 1
            fi

            echo "Converting ${AIRFLOW_TMP_DIR}/$outputFile_EN to ${AIRFLOW_TMP_DIR}/$transcriptFile_EN"
            python3 convert_result_to_asr_normalized_result.py --input-file "${AIRFLOW_TMP_DIR}/$outputFile_EN" --output-file "${AIRFLOW_TMP_DIR}/$transcriptFile_EN"
            retVal=$?
            if [ $retVal -ne 0 ]; then
                echo "Error during conversion of transcript for HAnS!"
                exit $retVal
            fi
            wordcount=$(wc -c ${AIRFLOW_TMP_DIR}/$transcriptFile_EN | awk '{print $1}')
            if [ "$wordcount" -lt 45 ]
            then
                echo "Error: Invalid transcript!"
                exit 1
            fi

            echo "Converting ${AIRFLOW_TMP_DIR}/$transcriptFile_EN to ${AIRFLOW_TMP_DIR}/$subtitleFile_EN"
            python3 convert_asr_normalized_result_to_webvtt.py --input-file "${AIRFLOW_TMP_DIR}/$transcriptFile_EN" --output-file "${AIRFLOW_TMP_DIR}/$subtitleFile_EN"
            retVal=$?
            if [ $retVal -ne 0 ]; then
                echo "Error during conversion of subtitle for HAnS!"
                exit $retVal
            fi
            wordcount=$(wc -c ${AIRFLOW_TMP_DIR}/$subtitleFile_EN | awk '{print $1}')
            if [ "$wordcount" -lt 7 ]
            then
                echo "Error: Invalid webvtt file!"
                exit 1
            fi
        fi

        if [[ $upload -eq 1 ]]; then
          url_upload_asr_result_DE=$(python3 parse_xcom.py "${UPLOAD_DATA_ASR_RESULT_DE}" "$uploadDataKeyAsrResult_DE")
          echo "Uploading $asrResultFile_DE to ${url_upload_asr_result_DE}"
          curl -X PUT "$url_upload_asr_result_DE" --upload-file "${AIRFLOW_TMP_DIR}/$asrResultFile_DE" -v

          url_upload_asr_result_EN=$(python3 parse_xcom.py "${UPLOAD_DATA_ASR_RESULT_EN}" "$uploadDataKeyAsrResult_EN")
          echo "Uploading $asrResultFile_EN to ${url_upload_asr_result_EN}"
          curl -X PUT "$url_upload_asr_result_EN" --upload-file "${AIRFLOW_TMP_DIR}/$asrResultFile_EN" -v

          url_upload_transcript_DE=$(python3 parse_xcom.py "${UPLOAD_DATA_TRANSCRIPT_DE}" "$uploadDataKeyTranscript_DE")
          echo "Uploading $transcriptFile_DE to ${url_upload_transcript_DE}"
          curl -X PUT "$url_upload_transcript_DE" --upload-file "${AIRFLOW_TMP_DIR}/$transcriptFile_DE" -v

          url_upload_transcript_EN=$(python3 parse_xcom.py "${UPLOAD_DATA_TRANSCRIPT_EN}" "$uploadDataKeyTranscript_EN")
          echo "Uploading $transcriptFile_EN to ${url_upload_transcript_EN}"
          curl -X PUT "$url_upload_transcript_EN" --upload-file "${AIRFLOW_TMP_DIR}/$transcriptFile_EN" -v

          url_upload_subtitle_DE=$(python3 parse_xcom.py "${UPLOAD_DATA_SUBTITLE_DE}" "$uploadDataKeySubtitle_DE")
          echo "Uploading $subtitleFile_DE to ${url_upload_subtitle_DE}"
          curl -X PUT "$url_upload_subtitle_DE" --upload-file "${AIRFLOW_TMP_DIR}/$subtitleFile_DE" -v

          url_upload_subtitle_EN=$(python3 parse_xcom.py "${UPLOAD_DATA_SUBTITLE_EN}" "$uploadDataKeySubtitle_EN")
          echo "Uploading $subtitleFile_EN to ${url_upload_subtitle_EN}"
          curl -X PUT "$url_upload_subtitle_EN" --upload-file "${AIRFLOW_TMP_DIR}/$subtitleFile_EN" -v
        fi
        echo '{"result": "finished"}'
    else
        printHelp
        exit 1
    fi
fi
