FROM alpine:3.6
RUN apk add --no-cache py3-pip python3
RUN pip3 install --no-cache-dir python-nomad prometheus_client
ADD exporter.py /tmp/
RUN adduser -S -h /app -u 1100 nomadexp
USER nomadexp
CMD ["/tmp/exporter.py"]
