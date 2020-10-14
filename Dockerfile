FROM registry:2.7.1

COPY requirements.txt /tmp/requirements.txt
COPY garbage-collector.py /garbage-collector.py
COPY lib /lib

RUN apk add --no-cache python3 py3-pip && \
    pip3 --no-cache-dir install -U pip && \
    pip3 --no-cache-dir install -r /tmp/requirements.txt

CMD [ "python3", "/garbage-collector.py" ]