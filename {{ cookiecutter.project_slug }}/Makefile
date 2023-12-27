bash:
	docker compose exec web bash

bash-root:
	docker compose exec -u root web bash

build:
	docker compose build

clean: stop
	docker compose down -v --remove-orphans

kill:
	docker compose kill
	docker compose rm --force

lint:
	docker compose exec web /app/lint.sh

logs:
	docker compose logs -f

migrate:
	docker compose exec web python manage.py migrate

migrations:
	docker compose exec web python manage.py makemigrations

shell:
	docker compose exec web python manage.py shell

start:
	UID=$${UID:-1000}
	GID=$${UID:-1000}
	mkdir -p docker/data/web docker/data/db{% if cookiecutter.enable_mailhog == "y" %} docker/data/mail{% endif %}{%- if cookiecutter.enable_celery == "y" or cookiecutter.enable_redis == "y" %} docker/data/messaging{% endif %}{% if cookiecutter.enable_minio == "y" %} docker/data/storage{% endif %}
	chown -R $$UID:$$GID docker/data/web docker/data/db{% if cookiecutter.enable_mailhog == "y" %} docker/data/mail{% endif %}{%- if cookiecutter.enable_celery == "y" or cookiecutter.enable_redis == "y" %} docker/data/messaging{% endif %}{% if cookiecutter.enable_minio == "y" %} docker/data/storage{% endif %}
	docker compose up -d

stop:
	docker compose down

restart: stop start

test:
	docker compose exec web pytest

test-v:
	docker compose exec web pytest -vvv

.PHONY: bash bash-root build clean kill lint logs migrate migrations shell start stop restart test test-v
