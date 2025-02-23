FROM python:3.12-slim-bookworm as base

RUN apt update \
    && apt install --no-install-recommends -y \
        gcc curl libgdal-dev wkhtmltopdf chromium-driver chromium \
    && apt clean && rm -rf /var/lib/apt/lists/* \
    && addgroup --system --gid 82 hcr \
    && adduser \
        --system --uid 82 \
        --disabled-password --home /home/hcr \
        --shell /sbin.nologin --group hcr --gecos hcr \
    && mkdir -p /code /tmp /data /static \
    && chown -R hcr:hcr /code /tmp /data /static

ENV PATH=$PATH:/code/.venv/bin/ \
    PACKAGES_DIR=/code/.venv/lib/python3.12/site-packages

WORKDIR /code

RUN curl -sSf https://raw.githubusercontent.com/astral-sh/uv/master/install.sh | sh

FROM base as builder

COPY ../pyproject.toml ./
RUN uv install
RUN uv sync --prod --no-editable

FROM builder AS dev

RUN uv sync --dev --no-editable

WORKDIR /code
COPY .. ./

COPY docker/entrypoint.sh /usr/local/bin/entrypoint.sh
ENTRYPOINT ["entrypoint.sh"]


FROM base AS prd

ENV DJANGO_SETTINGS_MODULE="hope_country_report.config.settings"

COPY --chown=hcr:hcr .. ./
COPY --chown=hcr:hcr --from=builder $PACKAGES_DIR $PACKAGES_DIR
USER hcr

COPY docker/entrypoint.sh /usr/local/bin/entrypoint.sh
ENTRYPOINT ["entrypoint.sh"]
