# Redis is limited to 7.2-bookworm due to licencing change
# https://redis.io/blog/redis-adopts-dual-source-available-licensing/
FROM redis:7.2-bookworm

# In production you might use TLS
#COPY redis.conf /usr/local/etc/redis/redis.conf
#CMD [ "redis-server", "/usr/local/etc/redis/redis.conf" ]
CMD [ "redis-server" ]
