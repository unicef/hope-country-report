DOCKER_IMAGE=hope-contry-report
VERSION?=dev

.build:
	cd .. && docker build \
			--cache-from "${DOCKER_IMAGE}:latest" \
			-t "${DOCKER_IMAGE}:${VERSION}" \
			-f docker/Dockerfile .
	#docker-squash "${DOCKER_IMAGE}:${TAG}-tmp" -t "${DOCKER_IMAGE}:${TAG}"

build: .build