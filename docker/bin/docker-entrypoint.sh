#!/bin/sh -e

export MEDIA_ROOT="${MEDIA_ROOT:-/var/run/app/media}"
export STATIC_ROOT="${STATIC_ROOT:-/var/run/app/static}"
export UWSGI_PROCESSES="${UWSGI_PROCESSES:-"4"}"
mkdir -p "${MEDIA_ROOT}" "${STATIC_ROOT}" || echo "Cannot create dirs ${MEDIA_ROOT} ${STATIC_ROOT}"

if [ -d "${MEDIA_ROOT}" ]; then
  chown -R hope:unicef "${MEDIA_ROOT}"
fi

if [ -d "${STATIC_ROOT}" ]; then
  chown -R hope:unicef "${STATIC_ROOT}"
fi

mkdir -p /app/
chown -R hope:unicef /app
cd /app

case "$1" in
    run)
        django-admin upgrade --with-check
        MAPPING=""
        if [ "${STATIC_URL}" = "/static/" ]; then
            MAPPING="--static-map ${STATIC_URL}=${STATIC_ROOT}"
        fi
        exec tini -- gosu hope:unicef uwsgi --http :8000 \
            -H /venv \
            --module hope_country_report.config.wsgi \
            --mimefile=/conf/mime.types \
            --uid hope \
            --gid unicef \
            --buffer-size 8192 \
            --http-buffer-size 8192 \
            $MAPPING
        ;;
    upgrade)
        exec django-admin upgrade --with-check
        ;;
    worker)
        exec tini -- gosu hope:unicef celery -A hope_country_report.config.celery worker \
            --concurrency=4 -E --loglevel=ERROR
        ;;
    pq-runner)
        # Service entrypoint — a separate Celery worker that is the only process allowed to execute Power Query previews.
        RUNNER_HOME="${RUNNER_HOME:-/var/run/app/runner}"
        mkdir -p "${RUNNER_HOME}/tmp" "${RUNNER_HOME}/.cache/matplotlib" || echo "Cannot create dirs ${RUNNER_HOME}"
        chown -R pqrunner:pqrunner "${RUNNER_HOME}" || echo "Cannot chown ${RUNNER_HOME}"
        export TMPDIR="${RUNNER_HOME}/tmp"
        export XDG_CACHE_HOME="${RUNNER_HOME}/.cache"
        export MPLCONFIGDIR="${RUNNER_HOME}/.cache/matplotlib"
        export POWER_QUERY_RUNNER="${POWER_QUERY_RUNNER:-1}"
        export POWER_QUERY_EXECUTION_MODE="${POWER_QUERY_EXECUTION_MODE:-runner}"
        exec tini -- gosu pqrunner:pqrunner celery -A hope_country_report.config.celery worker \
            --queues="${POWER_QUERY_RUNNER_QUEUE:-queue_hcr_power_query}" \
            --concurrency=1 -E --loglevel=ERROR
        ;;
    pq-uid)
        exec tini -- gosu pqrunner:pqrunner id
        ;;
    beat)
        exec tini -- gosu hope:unicef celery -A hope_country_report.config.celery beat \
            --loglevel=ERROR --scheduler django_celery_beat.schedulers:DatabaseScheduler
        ;;
    flower)
        export DATABASE_URL="sqlite://:memory:"
        exec tini -- gosu hope:unicef celery -A hope_country_report.config.celery flower
        ;;
    *)
        exec "$@"
        ;;
esac
