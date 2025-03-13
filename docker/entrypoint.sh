#!/bin/bash

set -eou pipefail

production() {
    waitforit -address=tcp://db:5432
    uwsgi \
        --http :8000 \
        --master \
        --module=src.hope_country_report.config.wsgi \
        --processes=2 \
        --buffer-size=8192
}

if [ $# -eq 0 ]; then
    production
fi

case "$1" in
    dev)
        waitforit -address=tcp://db:5432
        python3 manage.py migrate
        python3 manage.py runserver 0.0.0.0:8000
    ;;
    tests)
        waitforit -address=tcp://db:5432
        waitforit -address=tcp://hopedb:5432
        pytest tests/ --create-db --cov-report term -x  --with-selenium --strict-markers
    ;;
    prd)
        production
    ;;
    celery_worker)
        export C_FORCE_ROOT=1
        watchmedo auto-restart --directory=./ --pattern=*.py --recursive -- celery -A hope_country_report.config.celery worker -l info
    ;;
    celery_beat)
        waitforit -host=redis -port=6379
        celery -A hope_country_report.config.celery beat -l info
    ;;
    celery_flower)
        waitforit -address=tcp://backend:8000
        celery -A hope_country_report.config.celery flower
    ;;
    *)
        exec "$@"
    ;;
esac
