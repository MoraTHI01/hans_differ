# Ubuntu version
ARG VER=22.04

FROM ubuntu:${VER}

ENV DEBIAN_FRONTEND noninteractive
ENV TZ=Europe/Berlin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update \
    && apt-get -y --no-install-recommends install wget ca-certificates \
    && update-ca-certificates

RUN apt install -y tzdata

RUN apt-get -y update && apt-get -y upgrade && apt-get -y install -y \
curl \
python3.10 \
python3-pip \
git \
&& apt-get -y clean \
&& apt-get -y autoremove \
&& rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --upgrade pip

RUN apt-get -y update && apt-get -y upgrade && apt-get -y install -y \
build-essential \
yasm \
nasm \
cmake \
libtool \
bc \
unzip \
wget \
pkgconf \
libmp3lame-dev \
libtheora-dev \
libvorbis-dev \
libimage-exiftool-perl

WORKDIR /code
COPY . .
ENV LANG C.UTF-8

RUN cd /code && git clone http://git.videolan.org/git/x264.git x264 && cd x264 && git checkout stable
RUN cd /code/x264 && PKG_CONFIG_PATH="/usr/local/lib/pkgconfig" ./configure --enable-shared --enable-pic --extra-ldflags="-L/usr/local/lib/pkgconfig"
RUN cd /code/x264 && make -j 8 && make install

RUN cd /code && git clone https://chromium.googlesource.com/webm/libvpx libvpx && cd libvpx && git checkout tags/v1.14.1
RUN cd /code/libvpx && PKG_CONFIG_PATH="/usr/local/lib/pkgconfig" ./configure --enable-shared --enable-pic
RUN cd /code/libvpx && make -j 8 && make install

RUN cd /code && git clone https://git.ffmpeg.org/ffmpeg.git ffmpeg && cd ffmpeg && git checkout n5.1.6
RUN cd /code/ffmpeg && PKG_CONFIG_PATH="/usr/local/lib/pkgconfig" ./configure --enable-gpl --enable-version3 --enable-shared --enable-nonfree --enable-postproc --enable-libmp3lame --enable-libvpx --enable-libx264 --enable-libtheora --enable-libvorbis --extra-ldflags="-L/usr/local/lib/pkgconfig"
RUN cd /code/ffmpeg && make -j 8 && make install && ldconfig
RUN cd /code/ffmpeg/tools && make -j 8 qt-faststart && cp qt-faststart /usr/local/bin/

RUN python3 -m pip install minio
RUN cd /code && chmod +x parse_xcom.py && chmod +x upload_assetdb_temp.py && chmod +x download_assetdb_temp.py

RUN cd /code && chmod +x convert.sh && chmod +x create_dash.sh && chmod +x create_hls.sh
RUN cd /code && python3 -m pip install /code/modules/dist/hans_shared_modules-0.1-py3-none-any.whl
