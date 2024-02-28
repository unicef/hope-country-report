FROM python:3.11-slim-bookworm as base

RUN apt-get update \
    && apt-get install -y \
        gcc curl libgdal-dev wkhtmltopdf chromium-driver chromium \
    && apt-get clean && rm -rf /var/lib/apt/lists/* \
    && addgroup --system --gid 82 hcr \
    && adduser \
        --system --uid 82 \
        --disabled-password --home /home/hcr \
        --shell /sbin.nologin --group hcr --gecos hcr \
    && mkdir -p /code /tmp /data /static \
    && chown -R hcr:hcr /code /tmp /data /static

ENV PACKAGES_DIR=/packages
ENV PYPACKAGES=$PACKAGES_DIR/__pypackages__/3.11
ENV LIB_DIR=$PYPACKAGES/lib
ENV PYTHONPATH=$PYTHONPATH:$LIB_DIR:/code/src
ENV PATH=$PATH:$PYPACKAGES/bin

WORKDIR /code

FROM base as builder

WORKDIR $PACKAGES_DIR
RUN pip install pdm==2.10.4
ADD pyproject.toml ./
ADD pdm.toml.template ./pdm.toml
ADD pdm.lock ./
RUN pdm sync --prod --no-editable --no-self

FROM builder AS dev

RUN pdm sync --no-editable --no-self

WORKDIR /code
COPY ./ ./

ADD entrypoint.sh /usr/local/bin/entrypoint.sh
ENTRYPOINT ["entrypoint.sh"]


FROM base AS prd

ENV PATH=$PATH:/code/.venv/bin/

COPY --chown=hcr:hcr ./ ./
COPY --chown=hcr:hcr --from=builder $PACKAGES_DIR $PACKAGES_DIR
USER hcr

ADD entrypoint.sh /usr/local/bin/entrypoint.sh
ENTRYPOINT ["entrypoint.sh"]
