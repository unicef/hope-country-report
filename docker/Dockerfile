# syntax=docker/dockerfile:1.3
ARG PYTHON_VER=3.11
ARG PKG_DIR=/code/__pypackages__/$PYTHON_VER/lib
ARG BUILD_DATE
ARG CHECKSUM

FROM python:${PYTHON_VER}-slim-bullseye AS python

FROM python AS base
ARG PKG_DIR
ENV ADMINS="" \
    UWSGI_PROCESSES=4 \
    VERSION=${VERSION}

ENV PYTHONPATH=$PKG_DIR:/code/src/ \
    PATH=${PATH}:$PKG_DIR/../bin/

RUN ln -s -f /bin/true /usr/bin/chfn \
    && groupadd --gid 1024 sos \
    && adduser --disabled-login --disabled-password --no-create-home --ingroup sos -q www


FROM python AS cache
ARG PKG_DIR
ENV BUILD_DATE=$BUILD_DATE \
    VERSION=$VERSION \
    PYTHONDONTWRITEBYTECODE=1
ENV buildDeps="build-essential gcc libjpeg-dev zlib1g-dev libffi-dev libssl-dev libpq-dev "
ENV runtimeDeps="postgresql-client "
RUN rm -f /etc/apt/apt.conf.d/docker-clean \
    && echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache

RUN apt-get update

RUN apt-get install -y --no-install-recommends $buildDeps

RUN apt-get install -y --no-install-recommends $runtimeDeps

RUN rm -rf /var/lib/apt/lists/*
RUN pip install -U pip setuptools && pip install pdm

FROM cache AS builder
ARG PKG_DIR
ARG CHECKSUM
WORKDIR /code/
COPY pyproject.toml pdm.lock README.md /code/
RUN mkdir __pypackages__ \
    && pdm sync --prod --no-editable --no-self

RUN echo $CHECKSUM > /CHECKSUM


FROM builder AS builder-test
ARG PKG_DIR
WORKDIR /code/
ENV PYTHONPATH=$PKG_DIR:/code/src/ \
    PATH=${PATH}:$PKG_DIR/../bin/

RUN pdm sync --no-editable --no-self


FROM base AS dist
ARG PKG_DIR
COPY docker/bin/* /usr/local/bin/
COPY docker/conf/* /conf/
WORKDIR /code/
COPY --from=builder /code/__pypackages__ /code/__pypackages__
COPY --from=builder /CHECKSUM /CHECKSUM
COPY ./src /code/src

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["run"]


FROM base AS test
ARG PKG_DIR
COPY docker/bin/* /usr/local/bin/
COPY docker/conf/* /conf/
WORKDIR /code/
COPY --from=builder-test /code/__pypackages__ /code/__pypackages__
COPY --from=builder /CHECKSUM /CHECKSUM
COPY . /code/

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["run"]
