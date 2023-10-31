bash:
	docker compose exec web bash

bash-root:
	docker compose exec -u root web bash

build:
	docker compose build

lint:
	docker compose exec web /app/lint.sh

shell:
	docker compose exec web python manage.py shell

test:
	docker compose exec web pytest

test-v:
	docker compose exec web pytest -vvv

.PHONY: bash bash-root build lint shell test test-v
