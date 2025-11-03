FROM alpine:latest
RUN apk add --update socat bash && \
    rm -rf /var/cache/apk/*
COPY ./run.sh /
RUN chmod +x /run.sh
CMD ["/run.sh"]
