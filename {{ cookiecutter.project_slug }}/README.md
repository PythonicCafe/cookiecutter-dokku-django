# {{ cookiecutter.project_slug }}

You need docker compose to run this project.

Running all services:

```shell
docker compose up
```

To access Django, go to [localhost:5000](http://localhost:5000).
{%- if cookiecutter.enable_mailhog == "y" %}
To access Mailhog, go to [localhost:8025](http://localhost:5000).
{%- endif %}

Running the first migration:

```shell
docker compose exec web python manage.py migrate
```

Creating Django's super user:

```shell
docker compose exec web python manage.py createsuperuser
```
