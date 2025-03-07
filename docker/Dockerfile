FROM python:3.12-slim-bookworm AS base

RUN apt update && apt install --no-install-recommends -y \
        gcc curl libgdal-dev wkhtmltopdf chromium-driver chromium \
    && apt clean && rm -rf /var/lib/apt/lists/* \
    && addgroup --system --gid 82 hcr \
    && adduser \
        --system --uid 82 \
        --disabled-password --home /home/hcr \
        --shell /sbin.nologin --group hcr --gecos hcr \
    && mkdir -p /code /tmp /data /static \
    && chown -R hcr:hcr /code /tmp /data /static

ENV PATH=/venv/bin:/usr/local/bin/:/usr/bin:/bin \
    DJANGO_SETTINGS_MODULE=hope_country_report.config.settings \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_PROJECT_ENVIRONMENT=/venv \
    VIRTUAL_ENV=/venv \
    UWSGI_PROCESSES=4

RUN pip install uv uwsgi
WORKDIR /code

FROM base AS builder

RUN apt update \
    && apt install -y --no-install-recommends \
        build-essential cmake git libfontconfig1 libgconf-2-4 libglib2.0-0 libnss3 libssl-dev libxml2-dev python3-dev zlib1g-dev \
    && apt clean && rm -rf /var/lib/apt/lists/*


COPY pyproject.toml uv.lock /code/
COPY src /app/src/

RUN --mount=type=cache,target=/root/.uv-cache \
    uv sync --cache-dir=/root/.uv-cache \
        --python=/usr/local/bin/python \
        --python-preference=system \
        --frozen --link-mode=copy


FROM builder AS dev

ENV PYTHONPATH=$PYTHONPATH:/code/src:/code/test \
    PATH="/venv/bin:$PATH"

WORKDIR /code
COPY uv.lock README.md MANIFEST.in pyproject.toml /code/
COPY src /code/src/

COPY docker/entrypoint.sh /usr/local/bin/entrypoint.sh
ENTRYPOINT ["entrypoint.sh"]

FROM builder AS prd

ENV PATH="/code/.venv/bin:$PATH" \
    DJANGO_SETTINGS_MODULE="hope_country_report.config.settings" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UWSGI_PROCESSES=4

COPY --chown=hcr:hcr --from=builder $PACKAGES_DIR $PACKAGES_DIR
COPY --chown=hcr:hcr .. ./

USER hcr

COPY docker/entrypoint.sh /usr/local/bin/entrypoint.sh
ENTRYPOINT ["entrypoint.sh"]

FROM base AS dist

ENV PATH="/code/.venv/bin:$PATH" \
    DJANGO_SETTINGS_MODULE="hope_country_report.config.settings" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    STATIC_URL="/static/" \
    UWSGI_PROCESSES=4

COPY --chown=hcr:hcr --from=prd $PACKAGES_DIR $PACKAGES_DIR
COPY --chown=hcr:hcr .. ./

COPY docker/entrypoint.sh /usr/local/bin/entrypoint.sh
ENTRYPOINT ["entrypoint.sh"]
