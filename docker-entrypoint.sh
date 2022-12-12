#!/bin/bash -ex

exec consul-template \
  -consul-addr "${CONSUL_ADDRESS}" \
  -template /app/exporter.cfg.ctmpl:/app/exporter.cfg \
  -exec "python -u /usr/local/bin/prometheus-es-exporter $(echo $@)"
