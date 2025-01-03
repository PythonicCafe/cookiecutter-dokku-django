# Django build
FROM {{ cookiecutter.python_image }}:{{ cookiecutter.python_version }}

ENV PYTHONUNBUFFERED=1
ARG ENV_TYPE
WORKDIR /app
VOLUME /data

# Upgrade and install required system packages
RUN apt update \
  && apt install -y build-essential gettext gnupg make python3-dev wget \
{%- if cookiecutter.database_software == "postgres" %}
  && echo "deb http://apt.postgresql.org/pub/repos/apt bookworm-pgdg main" > /etc/apt/sources.list.d/pgdg.list \
  && wget --quiet -O /etc/apt/trusted.gpg.d/postgres.asc https://www.postgresql.org/media/keys/ACCC4CF8.asc \
  && apt update \
  && apt install -y postgresql-client-17 libpq-dev \
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

# Create a non-root user to run the app
RUN addgroup --gid ${GID:-1000} django \
  && adduser --disabled-password --gecos "" --home /app --uid ${UID:-1000} --gid ${GID:-1000} django \
  && chown -R django:django /app

# Upgrade pip and install (if needed) expensive-to-build, big packages and the ones from other indexes (for caching)
RUN pip install --no-cache-dir -U pip

# Install app requirements
COPY --chown=django:django requirements.txt /app/
COPY --chown=django:django requirements-development.txt /app/
RUN pip install --no-cache-dir -Ur /app/requirements.txt \
  && if [ "$(echo $ENV_TYPE | tr A-Z a-z)" = "development" ]; then pip install --no-cache-dir -Ur /app/requirements-development.txt; fi

# Copy all needed files and set permissions
COPY --chown=django:django . /app/
USER django
