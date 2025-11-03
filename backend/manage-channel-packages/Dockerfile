FROM debian:bookworm-slim
RUN apt-get -y update && apt-get -y upgrade \
 && apt-get install -y wget curl \
    python3 \
    python3-dev \
    python3-pip \
    python3-venv \
 && apt-get -y clean \
 && apt-get -y autoremove \
 && rm -rf /var/lib/apt/lists/*
WORKDIR /code
COPY . .
ENV LANG C.UTF-8

RUN pip install minio requests opensearch-py pymongo==4.6.3 apache-airflow-client uuid --break-system-packages && \
cd /code && chmod +x manage_channel_packages.py
