############################################################
# Dockerfile to build web frontend
############################################################

# build stage
FROM node:lts-alpine AS build-stage
WORKDIR /vue
COPY ./vue/package*.json ./
RUN npm install
COPY ./vue .
RUN npm run build

# production stage
FROM debian:bookworm-slim AS production-stage

RUN apt-get -y update && apt-get -y upgrade && apt-get -y install -y apache2 \
    libapache2-mod-wsgi-py3 \
    libapache2-mod-shib \
    build-essential \
    python3 \
    python3-dev \
    python3-pip \
    python3-venv \
    libaugeas0 \
    vim \
    nano \
    openssh-client \
    lsof \
    ffmpeg \
 && apt-get -y clean \
 && apt-get -y autoremove \
 && rm -rf /var/lib/apt/lists/*

# Copy the built vue app
COPY --from=build-stage /vue/dist /var/www/html

# Copy the flask app
COPY ./flask /var/www/flask
# Install flask requirements
RUN pip install -r /var/www/flask/requirements.txt --break-system-packages
# Copy the hans modules
COPY ./hans-modules /var/www/hans-modules
RUN pip install /var/www/hans-modules/dist/*.whl --break-system-packages

# Copy over the apache2 configuration files
COPY ./apache2/flask_apache2.conf /etc/apache2/sites-available/flask_apache2.conf
COPY ./apache2/vue_apache2.conf /etc/apache2/sites-available/vue_apache2.conf
COPY ./apache2/apache2.conf /etc/apache2/apache2.conf
COPY ./apache2/ports.conf /etc/apache2/ports.conf
COPY ./apache2/robots.txt /var/www/html/robots.txt
COPY ./apache2/security.txt /var/www/html/security.txt
## Temporary: using certbot (let's encrypt) to provide HTTPS
#RUN python3 -m venv /opt/certbot/ \
# && /opt/certbot/bin/pip install --upgrade pip \
# && /opt/certbot/bin/pip install certbot certbot-apache \
# && ln -s /opt/certbot/bin/certbot /usr/bin/certbot \
# && certbot --apache --test-cert --agree-tos --no-eff-email --email thomas.ranzenberger@th-nuernberg.de -d test.hans.th-nuernberg.de

# Enable the vue and flask sites
RUN a2dissite 000-default.conf
RUN a2ensite vue_apache2.conf
RUN a2ensite flask_apache2.conf

# Enable headers and ssl encryption
RUN a2enmod headers
RUN a2enmod ssl

# Enable proxy and rewrite modules
RUN a2enmod proxy
RUN a2enmod proxy_html
RUN a2enmod proxy_http
# RUN a2enmod proxy_wstunnel
RUN a2enmod rewrite
RUN a2enmod actions

# LINK apache config to docker logs.
RUN ln -sf /proc/self/fd/1 /var/log/apache2/access.log && \
    ln -sf /proc/self/fd/1 /var/log/apache2/error.log

EXPOSE 80 443 5001

WORKDIR /var/www

CMD  /usr/sbin/apache2ctl -D FOREGROUND
