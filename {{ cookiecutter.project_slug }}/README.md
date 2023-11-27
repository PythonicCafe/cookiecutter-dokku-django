# {{ cookiecutter.project_slug }}

You need docker compose to run this project.

Running all services:

```shell
make start
```

To access Django, go to [localhost:5000](http://localhost:5000).
{%- if cookiecutter.enable_mailhog == "y" %}
To access Mailhog, go to [localhost:8025](http://localhost:5000).
{%- endif %}

Running the first migration:

```shell
docker compose exec web python manage.py migrate
# or `make bash` and then `python manage.py migrate` inside the container
```

Creating Django's super user:

```shell
docker compose exec web python manage.py createsuperuser
# or `make bash` and then `python manage.py createsuperuser` inside the container
```

Running tests (outside container):

```shell
make test  # use test-v for verbose version of pytest
```

Force the Python code style guide/reformat all files (outside container):

```shell
make lint
```

## Backup

You may need to backup the following directories:
- `docker/data/web` in case your Web application stores user data in `/data` (or equivalent Dokku volume on production
  server)
- `docker/data/db` for the database (or equivalent Dokku volume on production server)
