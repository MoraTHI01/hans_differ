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

RUN python3 -m pip install minio --break-system-packages && \
python3 -m pip install -r requirements.txt --break-system-packages

RUN python3 -m spacy download en_core_web_trf && \
python3 -m spacy download en_core_web_md && \
python3 -m spacy download de_dep_news_trf && \
python3 -m spacy download de_core_news_md && \
python3 nlp_initialize.py

RUN cd /code && chmod +x parse_xcom.py && chmod +x upload_assetdb_temp.py && chmod +x download_assetdb_temp.py

RUN cd /code && chmod +x normalize.sh && chmod +x nlp_initialize.py && chmod +x nlp_normalize.py
RUN cd /code && python3 -m pip install /code/modules/dist/hans_shared_modules-0.1-py3-none-any.whl --break-system-packages
