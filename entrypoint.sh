#!/bin/bash

set -eou pipefail

export PYTHONPATH="$PYTHONPATH:/code/src" # without this, uwsgi can't load python modules

production() {
    python3 manage.py upgrade
    uwsgi \
        --http :8000 \
        --master \
        --module=src.hope_country_report.config.wsgi \
        --processes=2
}

if [ $# -eq 0 ]; then
    production
fi

case "$1" in
    dev)
        python3 manage.py migrate
        python3 manage.py runserver 0.0.0.0:8000
    ;;
    tests)
        sleep 10 # FIXME: hack to wait for postgis init
        python3 -m pytest --create-db
    ;;
    prd)
        production
    ;;
    *)
        exec "$@"
    ;;
esac