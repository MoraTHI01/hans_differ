#!/bin/bash

# MPEG-DASH is the new standard for Adaptive Bitrate Streaming
# See https://blog.zazu.berlin/internet-programmierung/mpeg-dash-and-hls-adaptive-bitrate-streaming-with-ffmpeg.html

INPUT_FILE=""
OUTPUT_FOLDER=""
singleResPreview=0

source ./settings.config
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib

while getopts hi:p:o:r:st:v flag
do
    case "${flag}" in
        h) showHelp=1;;
        i) create=1; INPUT_FILE=$OPTARG;;
        o) OUTPUT_FOLDER=$OPTARG;;
        p) PRESET_P=$OPTARG;;
        r) RESOLUTION=$OPTARG;;
        s) singleResPreview=1;;
        t) ffmpeg_threads=$OPTARG;;
        v) LOGLEVEL=verbose;;
    esac
done

if [[ $showHelp -eq 1 ]] || [[ $create -eq 0 ]]
then
    echo "Converts single mp4 video file to DASH streaming junks"
    echo "Usage:"
    echo "  create_dash.sh -i <input-file> -o <output-folder> [-r <resolution> -p <ffmpeg-preset> -v]"
    echo "Parameters: "
    echo "  -i: The input video file path"
    echo "  -p: Preset of ffmpeg, e.g. 'veryslow', 'slow', 'medium' or 'fast', default: 'slow'"
    echo "  -r: Resolution, 'full-hd' or 'hd', default: 'hd'"
    echo "  -s: Single resolution preview mode"
    echo "  -t: ffmpeg threads, '0' for optimal threads, '1' for single thread, '2', ..., default: '0'"
    echo "  -o: Output folder"
    echo "  -v: Verbose output"
    echo "Example:"
    echo "  create_dash.sh -i 33863e6f-0462-4a95-876f-df47b846e938.mp4 -o ./33863e6f-0462-4a95-876f-df47b846e938"
else
    echo "INPUT_FILE_PATH: $INPUT_FILE"
    echo "RESOLUTION: $RESOLUTION"
    echo ""
    arrIN=(${INPUT_FILE//// })
    inputFile=${arrIN[-1]}
    outputDashFile="${inputFile%.*}.dash.mpd"
    inputFileName=${INPUT_FILE##*/}
    echo "OUTPUT_DASH_FILE: $outputDashFile"
    echo ""
    prev_dir=$(pwd)
    cd "$OUTPUT_FOLDER"
    if [ "$RESOLUTION" == "hd" ]; then
        if [[ $singleResPreview -eq 1 ]]; then
            echo "CONVERTING VIDEO INTO DASH HD FORMAT FOR PREVIEW"
            echo ""
            ffmpeg -hide_banner -threads $ffmpeg_threads -i $INPUT_FILE -y \
                -c:v libx264 -preset $PRESET_P -keyint_min $GOP_SIZE -g $GOP_SIZE -sc_threshold 0 -r $FPS -pix_fmt yuv420p \
                -c:a aac -b:a $AUDIO_BITRATE -ac $AUDIO_CHANNELS -ar $AUDIO_SAMPLERATE \
                -map v:0 -b:v:0 $V_RATE_4 -maxrate:0 $V_RATE_MAX_4 -bufsize:0 $V_BUF_SIZE_4 -s:0 $V_SIZE_4 \
                -map 0:a \
                -init_seg_name ${inputFileName%.*}-i\$RepresentationID\$.\$ext\$ -media_seg_name ${inputFileName%.*}-c\$RepresentationID\$-\$Number%05d\$.\$ext\$ \
                -use_template 1 \
                -use_timeline 1 \
                -seg_duration 4 \
                -adaptation_sets "id=0,streams=v id=1,streams=a" \
                -target_latency 3 \
                -streaming 1 \
                -f dash "$outputDashFile" -v $LOGLEVEL
            echo ""
        else
            echo "CONVERTING VIDEO INTO DASH HD FORMAT"
            echo ""
            ffmpeg -hide_banner -threads $ffmpeg_threads -i $INPUT_FILE -y \
                -c:v libx264 -preset $PRESET_P -keyint_min $GOP_SIZE -g $GOP_SIZE -sc_threshold 0 -r $FPS -pix_fmt yuv420p \
                -c:a aac -b:a $AUDIO_BITRATE -ac $AUDIO_CHANNELS -ar $AUDIO_SAMPLERATE \
                -map v:0 -b:v:0 $V_RATE_0 -maxrate:0 $V_RATE_MAX_0 -bufsize:0 $V_BUF_SIZE_0 -s:0 $V_SIZE_0 \
                -map v:0 -b:v:1 $V_RATE_1 -maxrate:1 $V_RATE_MAX_1 -bufsize:1 $V_BUF_SIZE_1 -s:1 $V_SIZE_1 \
                -map v:0 -b:v:2 $V_RATE_2 -maxrate:2 $V_RATE_MAX_2 -bufsize:2 $V_BUF_SIZE_2 -s:2 $V_SIZE_2 \
                -map v:0 -b:v:3 $V_RATE_3 -maxrate:3 $V_RATE_MAX_3 -bufsize:3 $V_BUF_SIZE_3 -s:3 $V_SIZE_3 \
                -map v:0 -b:v:4 $V_RATE_4 -maxrate:4 $V_RATE_MAX_4 -bufsize:4 $V_BUF_SIZE_4 -s:4 $V_SIZE_4 \
                -map 0:a \
                -init_seg_name ${inputFileName%.*}-i\$RepresentationID\$.\$ext\$ -media_seg_name ${inputFileName%.*}-c\$RepresentationID\$-\$Number%05d\$.\$ext\$ \
                -use_template 1 \
                -use_timeline 1 \
                -seg_duration 4 \
                -adaptation_sets "id=0,streams=v id=1,streams=a" \
                -target_latency 3 \
                -streaming 1 \
                -f dash "$outputDashFile" -v $LOGLEVEL
            echo ""
        fi
    elif [ "$RESOLUTION" == "full-hd" ]; then
        if [[ $singleResPreview -eq 1 ]]; then
            echo "CONVERTING VIDEO INTO DASH FULL-HD FORMAT FOR PREVIEW"
            echo ""
            ffmpeg -hide_banner -threads $ffmpeg_threads -i $INPUT_FILE -y \
                -c:v libx264 -preset $PRESET_P -keyint_min $GOP_SIZE -g $GOP_SIZE -sc_threshold 0 -r $FPS -pix_fmt yuv420p \
                -c:a aac -b:a $AUDIO_BITRATE -ac $AUDIO_CHANNELS -ar $AUDIO_SAMPLERATE \
                -map 0:v \
                -map v:0 -b:v:0 $V_RATE_5 -maxrate:0 $V_RATE_MAX_5 -bufsize:0 $V_BUF_SIZE_5 -s:0 $V_SIZE_5 \
                -map 0:a \
                -init_seg_name ${inputFileName%.*}-i\$RepresentationID\$.\$ext\$ -media_seg_name ${inputFileName%.*}-c\$RepresentationID\$-\$Number%05d\$.\$ext\$ \
                -use_template 1 \
                -use_timeline 1 \
                -seg_duration 4 \
                -adaptation_sets "id=0,streams=v id=1,streams=a" \
                -target_latency 3 \
                -streaming 1 \
                -f dash "$outputDashFile" -v $LOGLEVEL
            echo ""
        else
            echo "CONVERTING VIDEO INTO DASH FULL-HD FORMAT"
            echo ""
            ffmpeg -hide_banner -threads $ffmpeg_threads -i $INPUT_FILE -y \
                -c:v libx264 -preset $PRESET_P -keyint_min $GOP_SIZE -g $GOP_SIZE -sc_threshold 0 -r $FPS -pix_fmt yuv420p \
                -c:a aac -b:a $AUDIO_BITRATE -ac $AUDIO_CHANNELS -ar $AUDIO_SAMPLERATE \
                -map 0:v \
                -map v:0 -b:v:0 $V_RATE_0 -maxrate:0 $V_RATE_MAX_0 -bufsize:0 $V_BUF_SIZE_0 -s:0 $V_SIZE_0 \
                -map v:0 -b:v:1 $V_RATE_1 -maxrate:1 $V_RATE_MAX_1 -bufsize:1 $V_BUF_SIZE_1 -s:1 $V_SIZE_1 \
                -map v:0 -b:v:2 $V_RATE_2 -maxrate:2 $V_RATE_MAX_2 -bufsize:2 $V_BUF_SIZE_2 -s:2 $V_SIZE_2 \
                -map v:0 -b:v:3 $V_RATE_3 -maxrate:3 $V_RATE_MAX_3 -bufsize:3 $V_BUF_SIZE_3 -s:3 $V_SIZE_3 \
                -map v:0 -b:v:4 $V_RATE_4 -maxrate:4 $V_RATE_MAX_4 -bufsize:4 $V_BUF_SIZE_4 -s:4 $V_SIZE_4 \
                -map v:0 -b:v:5 $V_RATE_5 -maxrate:5 $V_RATE_MAX_5 -bufsize:5 $V_BUF_SIZE_5 -s:5 $V_SIZE_5 \
                -map 0:a \
                -init_seg_name ${inputFileName%.*}-i\$RepresentationID\$.\$ext\$ -media_seg_name ${inputFileName%.*}-c\$RepresentationID\$-\$Number%05d\$.\$ext\$ \
                -use_template 1 \
                -use_timeline 1 \
                -seg_duration 4 \
                -adaptation_sets "id=0,streams=v id=1,streams=a" \
                -target_latency 3 \
                -streaming 1 \
                -f dash "$outputDashFile" -v $LOGLEVEL
            echo ""
        fi
    fi
    ret_val=0
    if [ -f ${outputDashFile} ]
    then
        if [ -s ${outputDashFile} ]
        then
            echo "File $outputDashFile exists and not empty"
        else
            echo "Error: File $outputDashFile exists but empty"
            ret_val=1
        fi
    else
        echo "Error: File $outputDashFile not exists"
        ret_val=1
    fi
    cd "$prev_dir"
    exit $ret_val
fi
