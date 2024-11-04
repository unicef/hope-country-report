#!/bin/bash

set -eou pipefail

production() {
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
        ./docker/wait-for-it.sh db:5432
        python3 manage.py migrate
        python3 manage.py runserver 0.0.0.0:8000
    ;;
    tests)
        ./docker/wait-for-it.sh db:5432
        pytest tests/ --create-db --cov-report term --maxfail 5 --with-selenium
    ;;
    prd)
        production
    ;;
    celery_worker)
        export C_FORCE_ROOT=1
        celery -A hope_country_report.config.celery worker -l info
    ;;
    celery_beat)
        celery -A hope_country_report.config.celery beat -l info
    ;;
    celery_flower)
        celery -A hope_country_report.config.celery flower
    ;;
    *)
        exec "$@"
    ;;
esac
