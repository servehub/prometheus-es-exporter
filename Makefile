VERSION?=$(shell git describe --tags --abbrev=0 | sed 's/v//')
TAG="kulikov/prometheus-es-exporter-consul"

release:
	@echo "==> Build and publish new docker image..."
	docker build -t ${TAG}:latest -t ${TAG}:${VERSION} .
	docker push ${TAG}:${VERSION}
	docker push ${TAG}:latest
