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
if [ -d "/app/src" ]; then
  chown -R hope:unicef /app/src
fi
cd /app

case "$1" in
    run)
        django-admin upgrade --with-check
        MAPPING=""
        if [ "${STATIC_URL}" = "/static/" ]; then
            MAPPING="--static-map ${STATIC_URL}=${STATIC_ROOT}"
        fi
        exec tini -- uwsgi --http :8000 \
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
    beat)
        exec tini -- gosu hope:unicef celery -A hope_country_report.config.celery beat \
            --loglevel=ERROR --scheduler django_celery_beat.schedulers:DatabaseScheduler
        ;;
    flower)
        export DATABASE_URL="sqlite://:memory:"
        exec tini -- gosu hope:unicef celery -A hope_country_report.config.celery flower
        ;;
    run_tests)
        exec tini -- gosu hope:unicef pytest tests/power_query/test_pq_utils.py --create-db -n auto -v --maxfail=5 --migrations --cov-report xml:./output/coverage.xml
        ;;
    *)
        echo "Unknown command: $1"
        exit 1
        ;;
esac
