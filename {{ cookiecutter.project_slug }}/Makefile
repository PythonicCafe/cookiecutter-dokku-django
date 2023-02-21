lint:
	autoflake --in-place --recursive --remove-unused-variables --remove-all-unused-imports .
	isort --skip migrations --skip wsgi --skip asgi --line-length {{ cookiecutter.max_line_length }} --multi-line VERTICAL_HANGING_INDENT --trailing-comma .
	black --exclude '(docker/|migrations/|config/settings\.py|manage\.py|\.direnv|\.eggs|\.git|\.hg|\.mypy_cache|\.nox|\.tox|\.venv|venv|\.svn|\.ipynb_checkpoints|_build|buck-out|build|dist|__pypackages__)' -l {{ cookiecutter.max_line_length }} .
	flake8 --config setup.cfg

test:
	docker compose exec web pytest

test-v:
	docker compose exec web pytest -vvv

.PHONY: lint test test-v
