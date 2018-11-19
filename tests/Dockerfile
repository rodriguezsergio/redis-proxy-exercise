FROM python:3.7.0

RUN pip install \
        aiohttp \
        aioredis

COPY *.py /opt/segment_tests/

WORKDIR /opt/segment_tests
CMD ["/usr/local/bin/python", "/opt/segment_tests/test.py"]
