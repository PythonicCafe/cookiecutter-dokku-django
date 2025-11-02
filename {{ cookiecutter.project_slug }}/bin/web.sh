#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

if [ -z ${PORT+x} ]; then
  PORT=5000
fi
if [ -z ${USE_ASGI+x} ]; then
  USE_ASGI=false
fi
if [ -z ${GUNICORN_WORKERS+x} ]; then
  GUNICORN_WORKERS={{ cookiecutter.gunicorn_workers }}
fi
if [ -z ${WEB_TIMEOUT+x} ]; then
  WEB_TIMEOUT=300
fi

HOST_PORT="0.0.0.0:$PORT"
OPTS="--bind=$HOST_PORT --chdir=/app --log-file - --access-logfile - --workers=$GUNICORN_WORKERS --timeout=$WEB_TIMEOUT"
if [[ "$(echo $USE_ASGI | tr a-z A-Z)" = "TRUE" ]]; then
  APP_MODULE="project.asgi:application"
  OPTS="$OPTS --worker-class uvicorn.workers.UvicornWorker"
else
  APP_MODULE="project.wsgi:application"
fi
if [[ $(echo $ENV_TYPE | tr A-Z a-z) = "development" ]]; then
  extra_reload_opts=$(
    find . -type f \
      \( \
        ! -path "./docker/data/*" \
        ! -path "./.git/*" \
        ! -path "./frontend/*" \
        ! -path "./.local/*" \
        ! -path "./.cache/*" \
      \) \
      -regex '.*\.\(html\|css\|js\|jpg\|gif\|png\|svg\|ttf\|woff\|woff2\|eot\|py\|json\)$' \
    | while read -r filename; do
        echo "--reload-extra-file $(dirname "$filename")"
    done | sort -u
  )
  OPTS="$OPTS --reload $extra_reload_opts"
fi

{% if cookiecutter.use_openai_client == "y" or cookiecutter.use_hugging_face == "y" %}
# Persist cache among containers
{% if cookiecutter.use_openai_client == "y" %}
TT_CACHE=${TIKTOKEN_CACHE_DIR:-}  # Avoid "unbound variable" error
if [[ ! -z "$TT_CACHE" ]] && [[ ! -e "$TT_CACHE" ]]; then
  mkdir -p "$TT_CACHE"
fi
{% endif %}
{% if cookiecutter.use_hugging_face == "y" %}
HF_CACHE=${HF_HUB_CACHE:-}  # Avoid "unbound variable" error
if [[ ! -z "$HF_CACHE" ]] && [[ ! -e "$HF_CACHE" ]]; then
  mkdir -p "$HF_CACHE"
fi
{% endif %}
{% endif %}

echo "Collecting static files"
python manage.py collectstatic --no-input

echo "Starting Web server"
gunicorn $OPTS $APP_MODULE
