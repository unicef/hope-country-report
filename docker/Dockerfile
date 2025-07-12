FROM python:3.13-slim-bookworm AS base_os

ARG GOSU_VERSION=1.17
ARG GOSU_SHA256=bbc4136d03ab138b1ad66fa4fc051bafc6cc7ffae632b069a53657279a450de3
ARG BUILD_DATE
ARG VERSION
ARG GIT_SHA

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgdal-dev libmagic1 libxml2 wkhtmltopdf tini wget && \
    wget -O /usr/local/bin/gosu "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-amd64" && \
    echo "$GOSU_SHA256 /usr/local/bin/gosu" | sha256sum --check --status && \
    chmod +x /usr/local/bin/gosu && \
    rm -rf /var/lib/apt/lists/*

RUN groupadd --gid 1024 unicef && \
    adduser --disabled-login --disabled-password --no-create-home --ingroup unicef -q hope

# ======= BUILDER =======
FROM base_os AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential cmake curl gcc git libfontconfig1 libgconf-2-4 \
    libglib2.0-0 libnss3 libssl-dev libxml2-dev python3-dev zlib1g-dev \
    gnupg unzip && \
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google.list && \
    apt-get update && apt-get install -y google-chrome-stable && \
    CHROME_VERSION=$(google-chrome --product-version) && \
    wget -q -P /chromedriver "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/$CHROME_VERSION/linux64/chromedriver-linux64.zip" && \
    unzip /chromedriver/chromedriver* -d /usr/local/bin/ && \
    rm -rf /var/lib/apt/lists/* /chromedriver

RUN pip install uv uwsgi && \
    python -m venv /venv

# ======= PRODUCTION =======
FROM builder AS production
WORKDIR /app
COPY pyproject.toml uv.lock README.md ./
COPY src ./src
COPY .git /app/.git/

ENV PATH=/venv/bin:/usr/local/bin/:/usr/bin:/bin \
    DJANGO_SETTINGS_MODULE=hope_country_report.config.settings \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_PROJECT_ENVIRONMENT=/venv \
    VIRTUAL_ENV=/venv \
    UWSGI_PROCESSES=4


RUN --mount=type=cache,target=/root/.uv-cache \
    uv sync --cache-dir=/root/.uv-cache \
        --python=/venv/bin/python \
        --python-preference=system \
        --no-dev --no-editable --frozen

RUN rm -rf /app/*

# ======= TESTS =======
FROM builder AS tests
WORKDIR /app
COPY --chown=hope:unicef . .

LABEL org.opencontainers.image.created="$BUILD_DATE"
LABEL org.opencontainers.image.version="$VERSION"

ENV PATH=/venv/bin:/usr/local/bin/:/usr/bin:/bin \
    DJANGO_SETTINGS_MODULE=hope_country_report.config.settings \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_PROJECT_ENVIRONMENT=/venv \
    VIRTUAL_ENV=/venv \
    UWSGI_PROCESSES=4 \
    TOX_WORKDIR=/app/.tox

RUN --mount=type=cache,target=/root/.uv-cache \
    uv sync --cache-dir=/root/.uv-cache \
        --python=/venv/bin/python \
        --python-preference=system \
        --frozen


COPY docker/bin/* /usr/local/bin/
ENTRYPOINT exec docker-entrypoint.sh "$0" "$@"

# ======= FINAL DIST =======
FROM base_os AS dist
ARG BUILD_DATE
ARG VERSION
ARG GIT_SHA
ARG BRANCH

ENV PATH="/venv/bin:/usr/local/bin/:/usr/bin:/bin:$PATH" \
    DJANGO_SETTINGS_MODULE="hope_country_report.config.settings" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UWSGI_PROCESSES=4

RUN <<EOF cat> /RELEASE
{"version": "$VERSION",
 "commit": "$GIT_SHA",
 "date": "$BUILD_DATE",
}
EOF
WORKDIR /app

COPY docker/conf /conf/
COPY docker/bin/* /usr/local/bin/
COPY --from=production /venv /venv
COPY --from=builder /usr/local/bin/uwsgi /usr/local/bin/uv /usr/local/bin/

LABEL distro="final"
LABEL maintainer="hope@unicef.org"
LABEL cheksum="$CHECKSUM"

LABEL org.opencontainers.image.authors="hope@unicef.org"
LABEL org.opencontainers.image.description="Hope Country Report"
LABEL org.opencontainers.image.documentation="https://github.com/unicef/hope-country-report/"
LABEL org.opencontainers.image.title="Hope Country Report"
LABEL org.opencontainers.image.licenses="${GITHUB_SERVER_URL}/${GITHUB_REPOSITORY}/blob/${GIT_SHA:-master}/LICENSE"
LABEL org.opencontainers.image.revision=$GIT_SHA
LABEL org.opencontainers.image.source="${GITHUB_SERVER_URL}/${GITHUB_REPOSITORY}/tree/${GIT_SHA:-master}/"
LABEL org.opencontainers.image.url="https://hub.docker.com/repository/docker/unicef/hope-country-report/tags/"
LABEL org.opencontainers.image.vendor="UNICEF"
LABEL org.opencontainers.image.created="$BUILD_DATE"
LABEL org.opencontainers.image.version="$VERSION"

EXPOSE 8000
ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["run"]
