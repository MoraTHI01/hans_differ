FROM adminer:4.8.1
ARG DEBIAN_FRONTEND=noninteractive
USER root
RUN apt-get update && apt-get install -y --no-install-recommends apt-utils \
    libssl-dev php-dev gnupg2 software-properties-common
# Adding the MongoDB GPG key
RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 9DA31620334BD75D9DCB49F368818C72E52529D4 \
    # Adding the MongoDB repository
    && add-apt-repository 'deb [arch=amd64] https://repo.mongodb.org/apt/ubuntu bionic/mongodb-org/4.0 multiverse' \
    && apt-get update && apt-get install -y mongodb-org
USER adminer
