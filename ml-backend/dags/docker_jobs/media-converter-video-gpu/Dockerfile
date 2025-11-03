# Ubuntu version
ARG VER=22.04
# CUDA version
ARG CUDA_VER=11.8.0

FROM --platform=linux/amd64 nvidia/cuda:${CUDA_VER}-devel-ubuntu${VER}

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
python3.10 \
python3-pip \
git \
build-essential \
yasm \
cmake \
libtool \
libc6 \
libc6-dev \
unzip \
wget \
libnuma1 \
libnuma-dev \
libssl-dev \
pkgconf \
libmp3lame-dev \
&& apt-get -y clean \
&& apt-get -y autoremove \
&& rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --upgrade pip

WORKDIR /code
COPY . .
ENV LANG C.UTF-8

RUN cd /code && git clone https://github.com/FFmpeg/nv-codec-headers.git nv-codec-headers && cd nv-codec-headers && git checkout n11.1.5.2
RUN cd /code && cd nv-codec-headers && make install
RUN cd /code && git clone https://git.ffmpeg.org/ffmpeg.git ffmpeg && cd ffmpeg && git checkout n5.1.6

RUN cd /code/ffmpeg && PKG_CONFIG_PATH="/usr/local/lib/pkgconfig" ./configure --enable-nonfree --enable-openssl --enable-libmp3lame --enable-cuda-nvcc --enable-cuvid --enable-nvenc --enable-nvdec --enable-cuda-llvm --enable-libnpp --extra-cflags="-I/usr/local/cuda/include -I/usr/local/include/ffnvcodec" --extra-ldflags="-L/usr/local/cuda/lib64 -L/usr/local/lib/pkgconfig" --disable-static --enable-shared
RUN cd /code/ffmpeg && make -j 8 && make install

RUN python3 -m pip install minio
RUN cd /code/modules/connectors && chmod -R +x * && \
cd /code && chmod +x parse_xcom.py && chmod +x upload_assetdb_temp.py && chmod +x download_assetdb_temp.py

RUN cd /code && chmod +x convert.sh && chmod +x create_dash.sh && chmod +x merge_dash.py
