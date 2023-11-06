bash:
	docker compose exec web bash

bash-root:
	docker compose exec -u root web bash

build:
	docker compose build

clean: stop
	docker compose down -v --remove-orphans

lint:
	docker compose exec web /app/lint.sh

logs:
	docker compose logs -f

shell:
	docker compose exec web python manage.py shell

start:
	docker compose up -d

stop:
	docker compose kill
	docker compose rm --force

test:
	docker compose exec web pytest

test-v:
	docker compose exec web pytest -vvv

.PHONY: bash bash-root build clean lint logs shell start stop test test-v
