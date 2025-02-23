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
    PACKAGES_DIR=/code/.venv/lib/python3.12/site-packages \
    PYTHONPATH=$PYTHONPATH:/code/src

WORKDIR /code

FROM base as builder

COPY ../pyproject.toml ./
COPY ../uv.lock ./

ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.local/bin/:$PATH"

RUN uv sync

FROM builder AS dev

WORKDIR /code
COPY .. ./

COPY docker/entrypoint.sh /usr/local/bin/entrypoint.sh
ENTRYPOINT ["entrypoint.sh"]


FROM base AS prd

ENV PATH=$PATH:/code/.venv/bin/
ENV DJANGO_SETTINGS_MODULE="hope_country_report.config.settings"

COPY --chown=hcr:hcr .. ./
COPY --chown=hcr:hcr --from=builder $PACKAGES_DIR $PACKAGES_DIR
USER hcr

COPY docker/entrypoint.sh /usr/local/bin/entrypoint.sh
ENTRYPOINT ["entrypoint.sh"]
