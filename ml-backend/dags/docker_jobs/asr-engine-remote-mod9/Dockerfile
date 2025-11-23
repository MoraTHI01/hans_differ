FROM debian:bookworm-slim

RUN apt-get -y update && apt-get -y upgrade && apt-get -y install -y\
 curl \
 python3 \
 python3-pip \
 && apt-get -y clean \
 && apt-get -y autoremove \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /code
COPY . .
ENV LANG C.UTF-8

RUN python3 -m pip install minio --break-system-packages
RUN cd /code && chmod +x parse_xcom.py && chmod +x upload_assetdb_temp.py && chmod +x download_assetdb_temp.py

RUN cd /code && chmod +x recognize.sh && chmod +x convert_to_asr_result.py
RUN cd /code && python3 -m pip install /code/modules/dist/hans_shared_modules-0.1-py3-none-any.whl --break-system-packages
