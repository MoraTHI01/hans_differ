FROM debian:bookworm-slim

RUN apt-get -y update && apt-get -y upgrade && apt-get -y install -y\
 curl \
 python3 \
 python3-pip \
 x264 \
 ffmpeg \
 && apt-get -y clean \
 && apt-get -y autoremove \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /code
COPY . .
ENV LANG C.UTF-8

RUN python3 -m pip install minio Pillow --break-system-packages
RUN cd /code && chmod +x parse_xcom.py && chmod +x upload_assetdb_temp.py && chmod +x download_assetdb_temp.py

RUN cd /code && chmod +x convert.sh && chmod +x thumbnails_count_to_timestamp.py && chmod +x convert_images.py
RUN cd /code && python3 -m pip install /code/modules/dist/hans_shared_modules-0.1-py3-none-any.whl --break-system-packages
