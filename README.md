# cookiecutter-dokku-django

A [cookiecutter](https://cookiecutter.readthedocs.io/) template for creating a Django project with deployment via
[Dokku](https://dokku.com/) (free/libre platform as a service).

Highlights:

- Base well-configured [Django](https://www.djangoproject.com/) with [PostgreSQL](https://postgres.org/).
- Efficiently serves Django with [gunicorn](https://gunicorn.org/) and
  [whitenoise](https://whitenoise.readthedocs.io/), optimizing request handling and static file management.
- Simplifies local development with [Docker Compose](https://docs.docker.com/compose/), eliminating virtualenv and
  Python version conflicts, while mirroring production services.
- Ensures environment consistency with identical `Dockerfile`, services, `settings.py`, and HTTP server across local
  and production.
- Provides sensible defaults, like `AutoField` over `BigAutoField` and suppressed `DisallowedHost` errors.
- Enforces consistent code style with `.editorconfig` (end-of-line, trailing spaces, indentation).
- Streamlines development with numerous `make` targets for a standardized workflow.
- Integrates linting with [black](https://black.readthedocs.io/en/stable/), [isort](https://pycqa.github.io/isort/),
  [autoflake](https://pypi.org/project/autoflake/), and [flake8](https://flake8.pycqa.org/en/latest/).
- Offers optional service integrations:
  - [MariaDB](https://mariadb.org/) as an alternative to [PostgreSQL](https://postgres.org/).
  - [Celery](https://docs.celeryq.dev/en/stable/) for background tasks.
  - [Redis](https://redis.io/) for task queue and/or cache (considering migrating to [Valkey](https://valkey.io/)
    because of [licensing
issues](https://arstechnica.com/information-technology/2024/04/redis-license-change-and-forking-are-a-mess-that-everybody-can-feel-bad-about/)).
  - [Mailhog](https://github.com/mailhog/MailHog) for local mail testing.
  - [MinIO](https://min.io/) for object storage.
- Includes a step-by-step markdown tutorial for [Dokku](https://dokku.com/) deployment.

## Using

First, install cookiecutter and render the template using your parameters:

```shell
pip install cookiecutter
cookiecutter gh:PythonicCafe/cookiecutter-dokku-django
# answer the questions :)
cd <project_slug>
git init .
git add -f .  # The only possible occasion where you're allowed to execute this command
git commit -m "First commit"
```

Then, read the created `<project_slug>/README.md` for local development instructions and
`<project_slug/docs/deploy.md>` for deployment instructions.


## To do

- [ ] Fix Dokku healthchecks (do not disable) while having `*` not in `ALLOWED_HOSTS` (use `httpHeaders` from
  [docker-container-healthchecker](https://github.com/dokku/docker-container-healthchecker))
- [ ] Add support for using [pydokku](https://github.com/PythonicCafe/pydokku/)
- [ ] Add a git pre-commit hook to automatically run tests, linter etc.
- [ ] Add plenty of possible email backends (SMTP, Sendgrid, Mailgun, AWS SES etc.)
- [ ] Add IMAP container for testing (something like
  [antespi/docker-imap-devel](https://github.com/antespi/docker-imap-devel) or
  [apache/james](https://hub.docker.com/r/apache/james))
- [ ] Configure workflows (CI/CD)
- [ ] Enhance `.dockerignore`
- [ ] Pin requirements' versions
- [ ] Replace `requirements.txt`/`requirements-development.txt` with other dependency file type
- [ ] Consolidate linter options in `pyproject.toml` or `setup.cfg` to make `lint.sh` more simple (or just use a couple
  of commands without options inside `Makefile`)
- [ ] Add option to multistage build when user needs to compile JS/CSS
- [ ] Translate `docs/deploy.md` to other languages (currently only available in Brazilian Portuguese)
- [ ] Check things we're missing that other implementations have, like
  [cookiecutter-django](https://cookiecutter-django.readthedocs.io/en/latest/),
  [cookiecutter-django-dokku](https://github.com/OpenUpSA/cookiecutter-django-dokku) and
  [django-boilerplate](https://github.com/HBNetwork/django-boilerplate)


## Updating PostgreSQL config file

If you want to change local postgres parameters so you can use less/more memory, workers etc.:

- Run `docker run --rm postgres:15-bullseye cat ./usr/share/postgresql/postgresql.conf.sample > "{{ cookiecutter.project_slug }}/docker/conf/db/postgresql.dev.conf"`
- Go to [pgtune.leopard.in.ua](https://pgtune.leopard.in.ua/), select your parameters and add to the end of
  `docker/conf/db/postgresql.dev.conf`

> Note: replace `postgres:15-bullseye` with the image/version you want to work with.

## License options

This repository is licensed under [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0.txt). When creating your
project based on this template you can choose one of the following license options:

- [GPL 3](https://www.gnu.org/licenses/gpl-3.0.txt)
- [LGPL 3](https://www.gnu.org/licenses/lgpl-3.0.txt)
- [AGPL 3](https://www.gnu.org/licenses/agpl-3.0.txt)
- [Apache 2](https://www.apache.org/licenses/LICENSE-2.0.txt)
- [MIT](https://opensource.org/licenses/MIT)
- [BSD](https://directory.fsf.org/wiki/License:BSD-3-Clause)
- Closed source

If you decide to use another license, just replace the `LICENSE` file after rendering the project.
