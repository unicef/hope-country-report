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

ENV PACKAGES_DIR=/packages
ENV PYPACKAGES=$PACKAGES_DIR/__pypackages__/3.12
ENV LIB_DIR=$PYPACKAGES/lib
ENV PYTHONPATH=$PYTHONPATH:$LIB_DIR:/code/src
ENV PATH=$PATH:$PYPACKAGES/bin

WORKDIR /code

FROM base as builder

WORKDIR $PACKAGES_DIR
RUN pip install pdm setuptools
COPY ../pyproject.toml ./
COPY ../pdm.lock ./
RUN pdm config python.use_venv false
RUN pdm config venv.in_project true
RUN pdm sync --prod --no-editable --no-self

FROM builder AS dev

RUN pdm sync --no-editable --no-self

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
