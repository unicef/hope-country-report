BASE_IMAGE?=hope-contry-report
CHECKSUM?=$(shell sha1sum ../uv.lock | awk '{print $$1}')
LOCK_SHA?=$(shell echo ${CHECKSUM} | cut -c 1-8)
COMMIT_SHA?=$(shell git rev-parse --short HEAD)
VERSION?=dev

.build:
	cd .. && docker build \
			--cache-from "${BASE_IMAGE}/builder:dev" \
			--cache-from "${BASE_IMAGE}:dev" \
			-t "${DOCKER_IMAGE}:${VERSION}" \
			${EXTRA} \
			-f docker/Dockerfile .

build:
	EXTRA='' \
	DOCKER_IMAGE="${BASE_IMAGE}" \
	VERSION=dev \
	TAG="${LOCK_SHA}" \
	$(MAKE) .build


target-builder:  ## build 'builder' image
	EXTRA='--target builder ' \
	DOCKER_IMAGE="${BASE_IMAGE}/builder" \
	TAG="${LOCK_SHA}" \
	$(MAKE) .build

.run:
	docker run \
		${RUN_OPTIONS} \
		-t "${DOCKER_IMAGE}:${VERSION}" \
		${CMD}

shell-target:  ## run production image
	DOCKER_IMAGE="${BASE_IMAGE}/$S" \
	VERSION=dev \
	RUN_OPTIONS=-it \
	CMD=/bin/bash \
	$(MAKE) .run
