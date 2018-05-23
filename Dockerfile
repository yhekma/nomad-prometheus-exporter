FROM alpine:3.6
RUN apk update
RUN apk add --no-cache python3 ca-certificates
ADD code /tmp/code
WORKDIR /tmp/code
RUN python3 setup.py install
RUN adduser -S -h /app -u 1100 nomadexp
USER nomadexp
CMD ["/usr/bin/exporter.py"]
