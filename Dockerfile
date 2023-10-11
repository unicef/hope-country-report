FROM python:3.11-slim-bullseye as base

RUN apt-get update \
    && apt-get install -y \
        gcc curl libgdal-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/* \
    && addgroup --system --gid 82 hcr \
    && adduser \
        --system --uid 82 \
        --disabled-password --home /home/hcr \
        --shell /sbin.nologin --group hcr --gecos hcr \
    && mkdir -p /code /tmp /data \
    && chown -R hcr:hcr /code /tmp /data

ENV PYTHONPYCACHEPREFIX=/tmp/pycache
ENV PYTHONPATH=$PYTHONPATH:/packages/.venv/lib/python3.11/site-packages

WORKDIR /code

FROM base as builder

WORKDIR /packages
RUN pip install pdm==2.9.3
ADD pyproject.toml /packages
ADD pdm.toml /packages
ADD pdm.lock /packages
RUN pdm sync --prod --no-editable --no-self

FROM builder AS dev

RUN pdm sync --no-editable --no-self

WORKDIR /code
COPY ./ ./

ADD entrypoint.sh /usr/local/bin/entrypoint.sh
ENTRYPOINT ["entrypoint.sh"]


FROM base AS prd

COPY --chown=hcr:hcr ./ ./
COPY --chown=hcr:hcr --from=builder $VIRTUAL_ENV $VIRTUAL_ENV
USER hcr

ADD entrypoint.sh /usr/local/bin/entrypoint.sh
ENTRYPOINT ["entrypoint.sh"]