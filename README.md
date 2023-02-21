# cookiecutter-dokku-django

A [cookiecutter](https://cookiecutter.readthedocs.io/) template for creating a Django app deployed by
[Dokku](https://dokku.com/) (free/libre platform as a service).

Some highlights:

- Serves the Django project using gunicorn + whitenoise
- Run all services locally using [docker compose](https://docs.docker.com/compose/), so no need to create virtualenv,
  mess with Python versions etc.
- Single `settings.py` so you won't have conflicts between local and production versions
- Sane defaults, such as `AutoField` (instead of `BigAutoField`), suppress `DissallowedHost` exception etc.
- Option to enable celery (+ redis), mailhog


## Using

First, install cookiecutter and render the template using your parameters:

```shell
pip install cookiecutter
cookiecutter gh:PythonicCafe/cookiecutter-dokku-django
# answer the questions :)
cd <project_slug>
git init .
git add .
git commit -m "First commit"
```

Then, read the created `<project_slug>/README.md` for local development instructions and `<project_slug/docs/deploy.md>`
for deployment instructions.


## To do

- [ ] Add a git pre-commit hook to automatically run tests, linter etc.
- [ ] Run containers as regular user so files created inside container will be acessible by current host user (there
  are a [plenty of hacks in this issue](https://github.com/docker/compose/issues/2380))
- [ ] Add `django_celery_beat` and `django_celery_results`?
- [ ] Add plenty of possible email backends (SMTP, Sendgrid, Mailgun, AWS SES etc.)
- [ ] Configure workflows (CI/CD)
- [ ] Enhance `.dockerignore`
- [ ] Pin requirements' versions
- [ ] Replace `requirements.txt`/`requirements-development.txt` with other dependency file type
- [ ] Add option to multistage build when user needs to compile JS
- [ ] Translate `docs/deploy.md` to other languages (currently only available in Brazilian Portuguese)
- [ ] Add more info about the docker compose services (paths, for example) on project's README
- [ ] Add option to configure AWS S3 and/or MinIO (add MinIO service to compose
  + settings)
- [ ] Check other implementations, like cookiecutter-django and https://github.com/HBNetwork/django-boilerplate


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
