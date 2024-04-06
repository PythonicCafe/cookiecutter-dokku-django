bash: start				# Run bash inside `web` container
	docker compose exec -it web bash

bash-root: start		# Run bash as root inside `web` container
	docker compose exec -itu root web bash

build:					# Build containers
	docker compose build

clean: stop				# Stop and clean orphan containers
	docker compose down -v --remove-orphans

dbshell: start			# Connect to database shell using `web` container
	docker compose exec -it web python manage.py dbshell

help:					# List all make commands
	@awk -F ':.*#' '/^[a-zA-Z_-]+:.*?#/ { printf "\033[36m%-15s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST) | sort

kill:					# Force stop (kill) and remove containers
	docker compose kill
	docker compose rm --force

lint:					# Run linter script
	docker compose exec -it web /app/lint.sh

logs:					# Show all containers' logs (tail)
	docker compose logs -tf

migrate:				# Execute Django migrations inside `web` container
	docker compose exec -it web python manage.py migrate

migrations:				# Execute `makemigrations` inside `web` container
	docker compose exec -it web python manage.py makemigrations

shell:					# Execute Django shell inside `web` container
	docker compose exec -it web python manage.py shell

restart: stop start		# Stop all containers and start all containers in background

start:					# Start all containers in background
	UID=$${UID:-1000}
	GID=$${UID:-1000}
	mkdir -p docker/data/web docker/data/db{% if cookiecutter.enable_mailhog == "y" %} docker/data/mail{% endif %}{%- if cookiecutter.enable_celery == "y" or cookiecutter.enable_redis == "y" %} docker/data/messaging{% endif %}{% if cookiecutter.enable_minio == "y" %} docker/data/storage{% endif %}
	chown -R $$UID:$$GID docker/data/web docker/data/db{% if cookiecutter.enable_mailhog == "y" %} docker/data/mail{% endif %}{%- if cookiecutter.enable_celery == "y" or cookiecutter.enable_redis == "y" %} docker/data/messaging{% endif %}{% if cookiecutter.enable_minio == "y" %} docker/data/storage{% endif %}
	docker compose up -d

stop:					# Stop all containers
	docker compose down

test:					# Execute `pytest` inside `web` container
	docker compose exec -it web pytest

test-v:					# Execute `pytest` with verbose option inside `web` container
	docker compose exec -it web pytest -vvv

.PHONY: bash bash-root build clean dbshell help kill lint logs migrate migrations restart shell start stop test test-v
