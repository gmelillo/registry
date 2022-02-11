FROM registry:2.8.0 as base

COPY requirements.txt /app/requirements.txt

RUN apk add --no-cache python3 py3-pip && \
    pip3 --no-cache-dir install -U pip && \
    pip3 --no-cache-dir install -r /app/requirements.txt && \
    rm -rf /root/.cache

FROM base as builder

COPY garbage-collector.py /app/garbage-collector.py
COPY lib /app/lib
COPY test /app/test
COPY test/kubeconfig /root/.kube/config

WORKDIR /app
RUN for i in /app/test/test_*.py; do basename="${i##*/}"; modules="${modules} ${basename%.py}"; done; PYTHONPATH="/app/lib:/app/test" python3 -m unittest ${modules}

COPY lib /out/app/lib
COPY garbage-collector.py /out/app/garbage-collector
RUN chmod +x /out/app/garbage-collector

FROM base

COPY --from=builder /out/ /

ENV GARBAGE_COLLECTOR_LOG_FORMAT=json

CMD [ "/app/garbage-collector" ]