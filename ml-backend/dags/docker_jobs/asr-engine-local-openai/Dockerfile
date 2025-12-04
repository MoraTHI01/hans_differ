# Ubuntu version
ARG VER=22.04
# CUDA version
ARG CUDA_VER=12.6.0

FROM --platform=linux/amd64 nvidia/cuda:${CUDA_VER}-runtime-ubuntu${VER}

ENV DEBIAN_FRONTEND noninteractive
ENV NVIDIA_VISIBLE_DEVICES all
ENV NVIDIA_DRIVER_CAPABILITIES compute,utility,video
ENV TZ=Europe/Berlin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update \
    && apt-get -y --no-install-recommends install wget ca-certificates \
    && update-ca-certificates
RUN apt install -y tzdata

RUN apt-get -y update && apt-get -y upgrade && apt-get -y install -y \
curl \
ffmpeg \
python3.10 \
python3-pip \
python3-dev \
git \
&& apt-get -y clean \
&& apt-get -y autoremove \
&& rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --upgrade pip

WORKDIR /code
COPY . .
ENV LANG C.UTF-8

RUN python3 -m pip install minio
RUN cd /code && chmod +x parse_xcom.py && chmod +x upload_assetdb_temp.py && chmod +x download_assetdb_temp.py

RUN cd /code && chmod +x recognize.sh \
&& chmod +x convert_asr_normalized_result_to_webvtt.py \
&& chmod +x convert_helpers.py \
&& chmod +x convert_whisper_result_to_asr_normalized_result.py \
&& chmod +x convert_whisper_result_to_asr_result.py \
&& chmod +x get_version.py \
&& chmod +x init_whisper.py

RUN cd /code && python3 -m pip install torch==2.0.1+cu118 torchaudio==2.0.2 --extra-index-url https://download.pytorch.org/whl/cu118
RUN cd /code && python3 -m pip install -r requirements.txt
RUN cd /code && python3 -m pip install /code/modules/dist/hans_shared_modules-0.1-py3-none-any.whl
RUN cd /code && python3 init_whisper.py medium
