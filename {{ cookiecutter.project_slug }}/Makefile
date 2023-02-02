lint:
	autoflake --in-place --recursive --remove-unused-variables --remove-all-unused-imports .
	isort --skip migrations --skip wsgi --skip asgi -rc .
	black . --exclude docker --exclude migrations -l {{ cookiecutter.max_line_length }}
	flake8 --config setup.cfg

test:
	docker compose exec web pytest

test-v:
	docker compose exec web pytest -vvv

.PHONY: lint test test-v
