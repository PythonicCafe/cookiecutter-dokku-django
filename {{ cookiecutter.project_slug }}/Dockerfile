FROM {{ cookiecutter.python_image }}:{{ cookiecutter.python_version }}

ENV PYTHONUNBUFFERED 1
ARG DEV_BUILD
WORKDIR /app
VOLUME /data

RUN apt update \
  && apt install -y build-essential gettext gnupg make python3-dev wget \
{%- if cookiecutter.database_software == "postgres" %}
  && echo "deb http://apt.postgresql.org/pub/repos/apt bullseye-pgdg main" > /etc/apt/sources.list.d/pgdg.list \
  && wget --quiet -O /etc/apt/trusted.gpg.d/postgres.asc https://www.postgresql.org/media/keys/ACCC4CF8.asc \
  && apt update \
  && apt install -y postgresql-client-15 libpq-dev \
{%- elif database_software == "mariadb" %}
                    pkg-config default-libmysqlclient-dev \
{%- endif %}
  && apt upgrade -y \
  && apt purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && apt clean \
  && rm -rf /var/lib/apt/lists/*
{%- if cookiecutter.apt_extra_packages != "" %}
RUN apt update \
  && apt upgrade -y \
  && apt install -y {{ cookiecutter.apt_extra_packages }} \
  && apt purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && apt clean \
  && rm -rf /var/lib/apt/lists/*
{%- endif %}

RUN addgroup --gid ${GID:-1000} django \
  && adduser --gid ${GID:-1000} --uid ${UID:-1000} --home=/app django \
  && chown -R django:django /app

COPY requirements.txt /app/
COPY requirements-development.txt /app/
RUN pip install --no-cache-dir -U pip \
  && pip install --no-cache-dir -Ur /app/requirements.txt \
  && if [ "$(echo $DEV_BUILD | tr A-Z a-z)" = "true" ]; then pip install --no-cache-dir -Ur /app/requirements-development.txt; fi


COPY . /app/
RUN chown -R django:django /app
USER django
