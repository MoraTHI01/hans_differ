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
EXPOSE 8087
RUN cd /code && chmod +x test.sh && pip install -r requirements.txt --break-system-packages && pip install -r ./api/tests/requirements.txt --break-system-packages
