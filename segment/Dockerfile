FROM python:3.7.0

RUN pip install \
        sanic \
        aioredis && \
    mkdir -p /opt/segment_app/logs

COPY *.py /opt/segment_app/
COPY segment.conf /etc/logrotate.d/

WORKDIR /opt/segment_app
CMD ["/usr/local/bin/python", "/opt/segment_app/segment.py"]
