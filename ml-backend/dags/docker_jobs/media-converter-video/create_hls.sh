#!/bin/bash

# HLS for Adaptive Bitrate Streaming
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
    echo "Converts single mp4 video file to HLS streaming junks"
    echo "Usage:"
    echo "  create_hls.sh -i <input-file> -o <output-folder> [-r <resolution> -p <ffmpeg-preset> -v]"
    echo "Parameters: "
    echo "  -i: The input video file path"
    echo "  -p: Preset of ffmpeg, e.g. 'veryslow', 'slow', 'medium' or 'fast', default: 'slow'"
    echo "  -r: Resolution, 'full-hd' or 'hd', default: 'hd'"
    echo "  -s: Single resolution preview mode"
    echo "  -t: ffmpeg threads, '0' for optimal threads, '1' for single thread, '2', ..., default: '0'"
    echo "  -o: Output folder"
    echo "  -v: Verbose output"
    echo "Example:"
    echo "  create_hls.sh -i 33863e6f-0462-4a95-876f-df47b846e938.mp4 -o ./33863e6f-0462-4a95-876f-df47b846e938"
else
    echo "INPUT_FILE_PATH: $INPUT_FILE"
    echo "RESOLUTION: $RESOLUTION"
    echo ""
    arrIN=(${INPUT_FILE//// })
    inputFile=${arrIN[-1]}
    inputFileName=${INPUT_FILE##*/}
    outputHLSFile="${inputFileName%.*}_%v.m3u8"
    outputHLSFileFinal="${inputFileName%.*}.m3u8"
    echo "OUTPUT_HLS_FILE: $outputHLSFileFinal"
    outputHLSSegmentFiles="${inputFileName%.*}_%v_%05d.ts"
    outputHLSSegmentFilesFinal="${inputFileName%.*}_0_%05d.ts"
    echo ""
    prev_dir=$(pwd)
    cd "$OUTPUT_FOLDER"

    if [ "$RESOLUTION" == "hd" ]; then
        if [[ $singleResPreview -eq 1 ]]; then
            echo "CONVERTING VIDEO INTO HLS HD FORMAT FOR PREVIEW"
            echo ""
            ffmpeg -hide_banner -threads $ffmpeg_threads -i $INPUT_FILE -y \
                -c:v libx264 -preset $PRESET_P -keyint_min $GOP_SIZE -g $GOP_SIZE -sc_threshold 0 -r $FPS -pix_fmt yuv420p \
                -c:a aac -b:a $AUDIO_BITRATE -ac $AUDIO_CHANNELS -ar $AUDIO_SAMPLERATE \
                -map 0:v:0 -map 0:a:0 \
                -filter:v:0 scale=$V_SIZE_FILTER_4  -b:v:0 $V_RATE_4 -maxrate:v:0 $V_RATE_MAX_4 -bufsize:v:0 $V_BUF_SIZE_4 -b:a:0 $AUDIO_BITRATE \
                -var_stream_map "v:0,a:0,name:$V_SIZE_NAME_4" \
                -hls_time 4 \
                -hls_playlist_type vod \
                -hls_flags independent_segments \
                -hls_segment_type mpegts \
                -hls_segment_filename "${outputHLSSegmentFiles}" \
                -master_pl_name "${outputHLSFileFinal}" \
                -f hls -v $LOGLEVEL "${outputHLSFile}"
            echo ""
        else
            echo "CONVERTING VIDEO INTO HLS HD FORMAT"
            echo ""
            ffmpeg -hide_banner -threads $ffmpeg_threads -i "$INPUT_FILE" -y \
                -c:v libx264 -preset "$PRESET_P" -keyint_min "$GOP_SIZE" -g "$GOP_SIZE" -sc_threshold 0 -r "$FPS" -pix_fmt yuv420p \
                -c:a aac -b:a "$AUDIO_BITRATE" -ac "$AUDIO_CHANNELS" -ar "$AUDIO_SAMPLERATE" \
                -map 0:v:0 -map 0:a:0 -map 0:v:0 -map 0:a:0 -map 0:v:0 -map 0:a:0 -map 0:v:0 -map 0:a:0 -map 0:v:0 -map 0:a:0 \
                -filter:v:0 scale=$V_SIZE_FILTER_0  -b:v:0 $V_RATE_0 -maxrate:v:0 $V_RATE_MAX_0 -bufsize:v:0 $V_BUF_SIZE_0 -b:a:0 $AUDIO_BITRATE \
                -filter:v:1 scale=$V_SIZE_FILTER_1  -b:v:1 $V_RATE_1 -maxrate:v:1 $V_RATE_MAX_1 -bufsize:v:1 $V_BUF_SIZE_1 -b:a:1 $AUDIO_BITRATE \
                -filter:v:2 scale=$V_SIZE_FILTER_2  -b:v:2 $V_RATE_2 -maxrate:v:2 $V_RATE_MAX_2 -bufsize:v:2 $V_BUF_SIZE_2 -b:a:2 $AUDIO_BITRATE \
                -filter:v:3 scale=$V_SIZE_FILTER_3  -b:v:3 $V_RATE_3 -maxrate:v:3 $V_RATE_MAX_3 -bufsize:v:3 $V_BUF_SIZE_3 -b:a:3 $AUDIO_BITRATE \
                -filter:v:4 scale=$V_SIZE_FILTER_4  -b:v:4 $V_RATE_4 -maxrate:v:4 $V_RATE_MAX_4 -bufsize:v:4 $V_BUF_SIZE_4 -b:a:4 $AUDIO_BITRATE \
                -var_stream_map "v:0,a:0,name:$V_SIZE_NAME_0 v:1,a:1,name:$V_SIZE_NAME_1 v:2,a:2,name:$V_SIZE_NAME_2 v:3,a:3,name:$V_SIZE_NAME_3 v:4,a:4,name:$V_SIZE_NAME_4" \
                -hls_time 4 \
                -hls_playlist_type vod \
                -hls_flags independent_segments \
                -hls_segment_type mpegts \
                -hls_segment_filename "${outputHLSSegmentFiles}" \
                -master_pl_name "${outputHLSFileFinal}" \
                -f hls -v "$LOGLEVEL" "${outputHLSFile}"
            echo ""
        fi
    elif [ "$RESOLUTION" == "full-hd" ]; then
        if [[ $singleResPreview -eq 1 ]]; then
            echo "CONVERTING VIDEO INTO HLS FULL-HD FORMAT FOR PREVIEW"
            echo ""
            ffmpeg -hide_banner -threads $ffmpeg_threads -i $INPUT_FILE -y \
                -c:v libx264 -preset $PRESET_P -keyint_min $GOP_SIZE -g $GOP_SIZE -sc_threshold 0 -r $FPS -pix_fmt yuv420p \
                -c:a aac -b:a $AUDIO_BITRATE -ac $AUDIO_CHANNELS -ar $AUDIO_SAMPLERATE \
                -map 0:v:0 -map 0:a:0 \
                -filter:v:0 scale=$V_SIZE_FILTER_5  -b:v:0 $V_RATE_5 -maxrate:v:0 $V_RATE_MAX_5 -bufsize:v:0 $V_BUF_SIZE_5 -b:a:0 $AUDIO_BITRATE \
                -var_stream_map "v:0,a:0,name:$V_SIZE_NAME_5" \
                -hls_time 4 \
                -hls_playlist_type vod \
                -hls_flags independent_segments \
                -hls_segment_type mpegts \
                -hls_segment_filename "${outputHLSSegmentFiles}" \
                -master_pl_name "${outputHLSFileFinal}" \
                -f hls -v "$LOGLEVEL" "${outputHLSFile}"
            echo ""
        else
            echo "CONVERTING VIDEO INTO HLS FULL-HD FORMAT"
            echo ""
            ffmpeg -hide_banner -threads $ffmpeg_threads -i $INPUT_FILE -y \
                -c:v libx264 -preset $PRESET_P -keyint_min $GOP_SIZE -g $GOP_SIZE -sc_threshold 0 -r $FPS -pix_fmt yuv420p \
                -c:a aac -b:a $AUDIO_BITRATE -ac $AUDIO_CHANNELS -ar $AUDIO_SAMPLERATE \
                -map 0:v:0 -map 0:a:0 -map 0:v:0 -map 0:a:0 -map 0:v:0 -map 0:a:0 -map 0:v:0 -map 0:a:0 -map 0:v:0 -map 0:a:0 \
                -filter:v:0 scale=$V_SIZE_FILTER_0  -b:v:0 $V_RATE_0 -maxrate:v:0 $V_RATE_MAX_0 -bufsize:v:0 $V_BUF_SIZE_0 -b:a:0 $AUDIO_BITRATE \
                -filter:v:1 scale=$V_SIZE_FILTER_1  -b:v:1 $V_RATE_1 -maxrate:v:1 $V_RATE_MAX_1 -bufsize:v:1 $V_BUF_SIZE_1 -b:a:1 $AUDIO_BITRATE \
                -filter:v:2 scale=$V_SIZE_FILTER_2  -b:v:2 $V_RATE_2 -maxrate:v:2 $V_RATE_MAX_2 -bufsize:v:2 $V_BUF_SIZE_2 -b:a:2 $AUDIO_BITRATE \
                -filter:v:3 scale=$V_SIZE_FILTER_3  -b:v:3 $V_RATE_3 -maxrate:v:3 $V_RATE_MAX_3 -bufsize:v:3 $V_BUF_SIZE_3 -b:a:3 $AUDIO_BITRATE \
                -filter:v:4 scale=$V_SIZE_FILTER_4  -b:v:4 $V_RATE_4 -maxrate:v:4 $V_RATE_MAX_4 -bufsize:v:4 $V_BUF_SIZE_4 -b:a:4 $AUDIO_BITRATE \
                -filter:v:5 scale=$V_SIZE_FILTER_5  -b:v:5 $V_RATE_5 -maxrate:v:5 $V_RATE_MAX_5 -bufsize:v:5 $V_BUF_SIZE_5 -b:a:5 $AUDIO_BITRATE \
                -var_stream_map "v:0,a:0,name:$V_SIZE_NAME_0 v:1,a:1,name:$V_SIZE_NAME_1 v:2,a:2,name:$V_SIZE_NAME_2 v:3,a:3,name:$V_SIZE_NAME_3 v:4,a:4,name:$V_SIZE_NAME_4 v:5,a:5,name:$V_SIZE_NAME_5" \
                -hls_time 4 \
                -hls_playlist_type vod \
                -hls_flags independent_segments \
                -hls_segment_type mpegts \
                -hls_segment_filename "${outputHLSSegmentFiles}" \
                -master_pl_name "${outputHLSFileFinal}" \
                -f hls -v $LOGLEVEL "${outputHLSFile}"
            echo ""
        fi
    fi

    ret_val=0
    if [ -f ${outputHLSFileFinal} ]
    then
        if [ -s ${outputHLSFileFinal} ]
        then
            echo "File $outputHLSFileFinal exists and not empty"
        else
            echo "Error: File $outputHLSFileFinal exists but empty"
            ret_val=1
        fi
    else
        echo "Error: File $outputHLSFileFinal not exists"
        ret_val=1
    fi
    cd "$prev_dir"
    exit $ret_val
fi
