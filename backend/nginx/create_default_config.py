#!/usr/bin/env python3

import sys


base_config = """server {
    listen ${NGINX_PORT};
    server_name ${NGINX_HOST};

    access_log off;
    error_log off;

    # To allow special characters in headers
    ignore_invalid_headers off;
    # Allow any size file to be uploaded.
    # Set to a value such as 1000m; to restrict file size to a specific value
    client_max_body_size 0;
    # To disable buffering
    proxy_buffering off;
    # To enable rewrite logging
    # error_log /var/log/nginx/error.log notice;
    # rewrite_log on;

    # Proxy requests to MinIO server "assetdb" running on port 9001
    location /assetdb {
      proxy_set_header X-Real-IP $remote_addr;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header X-Forwarded-Proto $scheme;
      proxy_set_header Host ${MINIO_ASSETDB_HOST}:${MINIO_ASSETDB_PORT};

      proxy_connect_timeout 300;
      # Default is HTTP/1, keepalive is only enabled in HTTP/1.1
      proxy_http_version 1.1;
      proxy_set_header Connection "";
      chunked_transfer_encoding off;

      proxy_pass http://${MINIO_ASSETDB_HOST}:${MINIO_ASSETDB_PORT}; # If you are using docker-compose this would be the hostname i.e. minio
      rewrite ^/assetdb(.*)$ $1 break;

      # Health Check endpoint might go here. See https://www.nginx.com/resources/wiki/modules/healthcheck/
      # /minio/health/live;
    }

    # Proxy requests to MinIO server "mediadb" running on port 9000
    location /mediadb {
      proxy_set_header X-Real-IP $remote_addr;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header X-Forwarded-Proto $scheme;
      proxy_set_header Host ${MINIO_MEDIADB_HOST}:${MINIO_MEDIADB_PORT};

      proxy_connect_timeout 300;
      # Default is HTTP/1, keepalive is only enabled in HTTP/1.1
      proxy_http_version 1.1;
      proxy_set_header Connection "";
      chunked_transfer_encoding off;

      proxy_pass http://${MINIO_MEDIADB_HOST}:${MINIO_MEDIADB_PORT}; # If you are using docker-compose this would be the hostname i.e. minio
      rewrite ^/mediadb(.*)$ $1 break;

      # Health Check endpoint might go here. See https://www.nginx.com/resources/wiki/modules/healthcheck/
      # /minio/health/live;
    }

    # Proxy requests to opensearch engine dashboard
    #location /searchengine-dashboard {
    #  proxy_set_header X-Real-IP $remote_addr;
    #  proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    #  proxy_set_header X-Forwarded-Proto $scheme;
    #  proxy_set_header Host searchengine-dashboard:5601;

    #  proxy_connect_timeout 300;
    #  proxy_read_timeout 90;
    #  # Default is HTTP/1, keepalive is only enabled in HTTP/1.1
    #  proxy_http_version 1.1;

    #  proxy_pass http://searchengine-dashboard:5601; # If you are using docker-compose this would be the hostname i.e. searchengine
    #  #rewrite ^(.*)/searchengine-dashboard(.*)$ $1 break;
    #}

    # Proxy requests to matomo
    location /matomo-analytics {
      rewrite ^/matomo-analytics$ /matomo-analytics/ permanent;
    }
    location /matomo-analytics/ {
      proxy_set_header X-Real-IP $remote_addr;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header X-Forwarded-Proto $scheme;
      proxy_set_header X-Forwarded-Uri /piwik;
      proxy_set_header Host ${MATOMO_HOST}:${MATOMO_PORT};

      proxy_redirect http://${NGINX_HOST}:${NGINX_PORT} http://${NGINX_HOST}:${NGINX_PORT}/matomo-analytics;

      proxy_pass http://${MATOMO_HOST}:${MATOMO_PORT}; # If you are using docker-compose this would be the hostname i.e. searchengine
      rewrite ^/matomo-analytics(.*)$ $1 break;
    }
"""

debug_config = """
    # Proxy requests to metadb-ui-backend
    location /metadb-ui-backend {
      proxy_set_header X-Real-IP $remote_addr;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header X-Forwarded-Proto $scheme;
      proxy_set_header Host metadb-ui-backend:8081;

      proxy_connect_timeout 300;
      # Default is HTTP/1, keepalive is only enabled in HTTP/1.1
      proxy_http_version 1.1;
      proxy_set_header Connection "";
      chunked_transfer_encoding off;

      proxy_pass http://metadb-ui-backend:8081; # If you are using docker-compose this would be the hostname i.e. searchengine
    }
"""

outp = open("nginx/default.conf.template", "w", encoding="utf-8")
outp.write(base_config)
if sys.argv[1] == "1":
    outp.write(debug_config)
outp.write("}\n")
outp.close()
