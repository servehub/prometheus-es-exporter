# Pin to 3.6, as prometheus-client has a memory leak in 3.7
# https://github.com/prometheus/client_python/issues/340
# TODO: unpin when patched prometheus-client version is released
FROM python:3.6-slim

RUN apt-get update \
    && apt-get install -y wget \
    && apt-get clean

RUN wget -O /tmp/consul-template.tgz https://releases.hashicorp.com/consul-template/0.18.5/consul-template_0.18.5_linux_amd64.tgz \
    && tar -xf /tmp/consul-template.tgz -C /usr/local/bin/ \
    && rm -f /tmp/consul-template.tgz

WORKDIR /app

ENV ES_QUERY_INDICES "<logstash-{now/d}>"

EXPOSE 9206

ENTRYPOINT ["/app/docker-entrypoint.sh"]

COPY setup.py /app/
RUN pip install .

COPY prometheus_es_exporter/*.py /app/prometheus_es_exporter/
RUN pip install -e .

COPY exporter.cfg.ctmpl docker-entrypoint.sh /app/
