#!/bin/bash

# MPEG-DASH is the new standard for Adaptive Bitrate Streaming
# See https://blog.zazu.berlin/internet-programmierung/mpeg-dash-and-hls-adaptive-bitrate-streaming-with-ffmpeg.html and
# https://mattcrook.io/41300/transcoding-to-dash-and-hls-with-ffmpeg
# https://stackoverflow.com/questions/67674772/ffmpeg-dash-ll-creates-audio-and-video-chunks-at-different-rates-player-is-conf

# Splitted gpu encoding two multiple ffmpeg calls, to not run out of gpu memory and to not exceed
# max concurrent streams: https://developer.nvidia.com/video-encode-and-decode-gpu-support-matrix-new

INPUT_FILE=""
OUTPUT_FOLDER=""
FPS=24
# GOP SIZE was: 100
GOP_SIZE=96
# PRESET_P was: veryslow , see https://write.corbpie.com/ffmpeg-preset-comparison-x264-2019-encode-speed-and-file-size/
PRESET_P=slow
AUDIO_CHANNELS=1
AUDIO_SAMPLERATE=44100
RESOLUTION="hd"
LOGLEVEL=info
# 0 = default = optimal = all, 1 (single-threaded), 2 (2 threads for e.g. an Intel Core 2 Duo);
ffmpeg_threads=0
singleResPreview=0

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
    outputDashFilePart0="${inputFile%.*}.dash.part0.mpd"
    outputDashFilePart1="${inputFile%.*}.dash.part1.mpd"
    inputFileName=${INPUT_FILE##*/}
    echo "OUTPUT_DASH_FILE: $outputDashFile"
    echo ""
    prev_dir=$(pwd)
    cd "$OUTPUT_FOLDER"

    if [[ $singleResPreview -eq 1 ]]; then
        if [ "$RESOLUTION" == "hd" ]; then
            echo "CONVERTING VIDEO INTO DASH HD FORMAT FOR PREVIEW"
            echo ""
            ffmpeg -hide_banner -threads $ffmpeg_threads -hwaccel cuvid -hwaccel_output_format cuda -c:v h264_cuvid -i $INPUT_FILE -y \
                -filter_complex "[0:v]scale_npp=-1:720[v720];" \
                -map "[v720]" -c:v h264_nvenc -b:v 3M -maxrate:v 4M -bufsize:v 6M -profile:v high -preset:v $PRESET_P -g:v $GOP_SIZE -keyint_min $GOP_SIZE -no-scenecut 1 -r $FPS -surfaces 40 \
                -c:a aac -b:a 256k -ac $AUDIO_CHANNELS -ar $AUDIO_SAMPLERATE \
                -map 0:a \
                -init_seg_name ${inputFileName%.*}-p1-i\$RepresentationID\$.\$ext\$ \
                -media_seg_name ${inputFileName%.*}-p1-c\$RepresentationID\$-\$Number%05d\$.\$ext\$ \
                -use_template 1 \
                -use_timeline 1 \
                -seg_duration 4 \
                -adaptation_sets "id=0,streams=v id=1,streams=a" \
                -f dash "$outputDashFile" -v $LOGLEVEL
        elif [ "$RESOLUTION" == "full-hd" ]; then
            echo "CONVERTING VIDEO INTO DASH FULL-HD FORMAT FOR PREVIEW"
            echo ""
            ffmpeg -hide_banner -threads $ffmpeg_threads -hwaccel cuvid -hwaccel_output_format cuda -c:v h264_cuvid -i $INPUT_FILE -y \
                -filter_complex "[0:v]scale_npp=-1:1080[v1080];" \
                -map "[v1080]" -c:v h264_nvenc -b:v 6M -maxrate:v 8M -bufsize:v 12M -profile:v high -preset:v $PRESET_P -g:v $GOP_SIZE -keyint_min $GOP_SIZE -no-scenecut 1 -r $FPS -surfaces 40 \
                -c:a aac -b:a 256k -ac $AUDIO_CHANNELS -ar $AUDIO_SAMPLERATE \
                -map 0:a \
                -init_seg_name ${inputFileName%.*}-p1-i\$RepresentationID\$.\$ext\$ \
                -media_seg_name ${inputFileName%.*}-p1-c\$RepresentationID\$-\$Number%05d\$.\$ext\$ \
                -use_template 1 \
                -use_timeline 1 \
                -seg_duration 4 \
                -adaptation_sets "id=0,streams=v id=1,streams=a" \
                -f dash "$outputDashFile" -v $LOGLEVEL
        fi
    else
        echo "CONVERTING VIDEO INTO DASH FORMAT BASE RESOLUTIONS"
        echo ""
        ffmpeg -hide_banner -threads $ffmpeg_threads -hwaccel cuvid -hwaccel_output_format cuda -c:v h264_cuvid -i $INPUT_FILE -y \
            -filter_complex "[0:v]scale_npp=-1:480[v480];[0:v]scale_npp=-1:360[v360];[0:v]scale_npp=-1:240[v240]" \
            -map "[v480]" -c:v h264_nvenc -b:v 1M -maxrate:v 2M -bufsize:v 3M -profile:v high -preset:v $PRESET_P -g:v $GOP_SIZE -keyint_min $GOP_SIZE -no-scenecut 1 -r $FPS -surfaces 40 \
            -map "[v360]" -c:v h264_nvenc -b:v 365k -maxrate:v 500k -bufsize:v 1M -profile:v high -preset:v $PRESET_P -g:v $GOP_SIZE -keyint_min $GOP_SIZE -no-scenecut 1 -r $FPS -surfaces 40 \
            -map "[v240]" -c:v h264_nvenc -b:v 145k -maxrate:v 200k -bufsize:v 400k -profile:v high -preset:v $PRESET_P -g:v $GOP_SIZE -keyint_min $GOP_SIZE -no-scenecut 1 -r $FPS -surfaces 40 \
            -c:a aac -b:a 128k -ac $AUDIO_CHANNELS -ar $AUDIO_SAMPLERATE \
            -map 0:a \
            -init_seg_name ${inputFileName%.*}-p0-i\$RepresentationID\$.\$ext\$ \
            -media_seg_name ${inputFileName%.*}-p0-c\$RepresentationID\$-\$Number%05d\$.\$ext\$ \
            -use_template 1 \
            -use_timeline 1 \
            -seg_duration 4 \
            -adaptation_sets "id=0,streams=v id=1,streams=a" \
            -f dash "$outputDashFilePart0" -v $LOGLEVEL

        if [ "$RESOLUTION" == "hd" ]; then
            echo "CONVERTING VIDEO INTO DASH HD FORMAT"
            echo ""
            ffmpeg -hide_banner -threads $ffmpeg_threads -hwaccel cuvid -hwaccel_output_format cuda -c:v h264_cuvid -i $INPUT_FILE -y \
                -filter_complex "[0:v]scale_npp=-1:720[v720];[0:v]scale_npp=-1:540[v540]" \
                -map "[v720]" -c:v h264_nvenc -b:v 3M -maxrate:v 4M -bufsize:v 6M -profile:v high -preset:v $PRESET_P -g:v $GOP_SIZE -keyint_min $GOP_SIZE -no-scenecut 1 -r $FPS -surfaces 40 \
                -map "[v540]" -c:v h264_nvenc -b:v 2M -maxrate:v 3M -bufsize:v 4M -profile:v high -preset:v $PRESET_P -g:v $GOP_SIZE -keyint_min $GOP_SIZE -no-scenecut 1 -r $FPS -surfaces 40 \
                -c:a aac -b:a 256k -ac $AUDIO_CHANNELS -ar $AUDIO_SAMPLERATE \
                -map 0:a \
                -init_seg_name ${inputFileName%.*}-p1-i\$RepresentationID\$.\$ext\$ \
                -media_seg_name ${inputFileName%.*}-p1-c\$RepresentationID\$-\$Number%05d\$.\$ext\$ \
                -use_template 1 \
                -use_timeline 1 \
                -seg_duration 4 \
                -adaptation_sets "id=0,streams=v id=1,streams=a" \
                -f dash "$outputDashFilePart1" -v $LOGLEVEL
            echo ""
        elif [ "$RESOLUTION" == "full-hd" ]; then
            echo "CONVERTING VIDEO INTO DASH FULL-HD FORMAT"
            echo ""
            ffmpeg -hide_banner -threads $ffmpeg_threads -hwaccel cuvid -hwaccel_output_format cuda -c:v h264_cuvid -i $INPUT_FILE -y \
                -filter_complex "[0:v]scale_npp=-1:1080[v1080];[0:v]scale_npp=-1:720[v720];[0:v]scale_npp=-1:540[v540]" \
                -map "[v1080]" -c:v h264_nvenc -b:v 6M -maxrate:v 8M -bufsize:v 12M -profile:v high -preset:v $PRESET_P -g:v $GOP_SIZE -keyint_min $GOP_SIZE -no-scenecut 1 -r $FPS -surfaces 40 \
                -map "[v720]" -c:v h264_nvenc -b:v 3M -maxrate:v 4M -bufsize:v 6M -profile:v high -preset:v $PRESET_P -g:v $GOP_SIZE -keyint_min $GOP_SIZE -no-scenecut 1 -r $FPS -surfaces 40 \
                -map "[v540]" -c:v h264_nvenc -b:v 2M -maxrate:v 3M -bufsize:v 4M -profile:v high -preset:v $PRESET_P -g:v $GOP_SIZE -keyint_min $GOP_SIZE -no-scenecut 1 -r $FPS -surfaces 40 \
                -c:a aac -b:a 256k -ac $AUDIO_CHANNELS -ar $AUDIO_SAMPLERATE \
                -map 0:a \
                -init_seg_name ${inputFileName%.*}-p1-i\$RepresentationID\$.\$ext\$ \
                -media_seg_name ${inputFileName%.*}-p1-c\$RepresentationID\$-\$Number%05d\$.\$ext\$ \
                -use_template 1 \
                -use_timeline 1 \
                -seg_duration 4 \
                -adaptation_sets "id=0,streams=v id=1,streams=a" \
                -f dash "$outputDashFilePart1" -v $LOGLEVEL
            echo ""
        fi
        echo "Merging $outputDashFilePart0 and $outputDashFilePart1 to $outputDashFile"
        python3 $prev_dir/merge_dash.py --input-base-file "$outputDashFilePart0" --input-additional-file "$outputDashFilePart1" --output-file "$outputDashFile"
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
