# {{ cookiecutter.project_slug }}

This project and all required services (as the database) run inside Docker containers. You'll need Docker, Docker
compose and make to run locally.

There are other ways to run the project locally (such as executing Django inside a virtualenv on the host machine), but
it's recommended to run the way described in this document to simplify the process and avoid version conflicts.

You need docker compose to run this project.

Running all services:

```shell
make start logs
```

> Note: the first time the command above is executed, it will take a few minutes because it will build the Docker image
> that runs Django and download the other images/dependencies. Subsequent runs will be much faster.

To access Django, go to [localhost:5000](http://localhost:5000). The `web` Docker compose service will automatically
execute the migrations before starting the HTTP server, so the system will be ready to be used.

Creating Django's super user:

```shell
docker compose exec -it web python manage.py createsuperuser
# or `make bash` and then `python manage.py createsuperuser` inside the container
```

Running tests (outside container):

```shell
make test
```

If you'd like to run just one the tests or pass options to `pytest`, set `TEST_ARGS`:
```shell
TEST_ARGS="-k test_run_only_this_one" make test
```

Force the Python code style guide/reformat all files (outside container):

```shell
make lint
```

For more commands check `make help`.


## Customizing environment variables

For each service we have a default environment file named `docker/env/<service>`. If you need to change any of the
default variables, create a file `docker/env/<service>.local` and put them there. This file will be ignored by Git and
docker compose will load it right after the default one (overwriting the values with your version).  This way we avoid
adding credentials and other sensitive data to the repository.

**Warning**: don't forget to run `make restart` for the environment variable changes to take effect (it's not enough to
restart only the container of the service whose variables were changed - you need to restart the entire Docker Compose
setup).

> Note: if you need to add a new environment variable that will be used by the whole team, define at least a dummy
> value in the main env file for the service, so everyone can run the system correctly.


## Backup

You may need to backup the following directories (or the equivalent Dokku directories in production):
- `docker/data/web` in case your Web application stores user data in `/data`
- `docker/data/db` for the database
{%- if cookiecutter.enable_minio == "y" %}
- `docker/data/storage` for the MinIO files
{%- endif %}


## Services

The services configured on Docker compose are:

- `web`: Django container, acessible through [localhost:5000](http://localhost:5000/)
{%- if cookiecutter.enable_celery == "y" %}
- `worker`: Django container, but running Celery worker (instead of gunicorn)
{%- endif %}
- `db`: database container, without port forwarding from the host machine (you can connect to the database shell by
  running `docker compose exec web python manage.py dbshell`)
{%- if cookiecutter.enable_mailhog == "y" %}
- `mail`: Mailhog container, acessible through [localhost:8025](http://localhost:8025)
{%- endif %}
{%- if cookiecutter.enable_redis == "y" %}
- `messaging`: redis container, without port forwarding from the host machine (you can connect to it by running
  `docker compose exec messaging redis-cli`)
{%- endif %}
{%- if cookiecutter.enable_minio == "y" %}
- `storage`: MinIO container, acessible through [localhost:9000](http://localhost:9000/) (API) and
  [localhost:9001](http://localhost:9001/) (console)
{%- endif %}
