VERSION?=$(shell git describe --tags --abbrev=0 | sed 's/v//')
TAG="servehub/prometheus-es-exporter-consul"

release:
	@echo "==> Build and publish new docker image..."
	docker build --platform=amd64 -t ${TAG}:latest -t ${TAG}:${VERSION} .
	docker push ${TAG}:${VERSION}
	docker push ${TAG}:latest
