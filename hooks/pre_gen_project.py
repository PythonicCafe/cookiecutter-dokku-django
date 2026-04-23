import json
import sys
from collections import OrderedDict  # noqa
from pathlib import Path


def validate_redis_implication():
    """Celery and Channels both require Redis as broker/channel layer - fail fast if it is disabled."""
    celery = "{{ cookiecutter.enable_celery }}".strip().lower() == "y"
    channels = "{{ cookiecutter.enable_channels }}".strip().lower() == "y"
    redis = "{{ cookiecutter.enable_redis }}".strip().lower() == "y"
    if (celery or channels) and not redis:
        reasons = []
        if celery:
            reasons.append("enable_celery=y")
        if channels:
            reasons.append("enable_channels=y")
        msg = f"ERROR: enable_redis must be y when {' or '.join(reasons)}. Re-run cookiecutter with enable_redis=y."
        print(msg, file=sys.stderr)
        sys.exit(1)


def save_answers():
    answers = {key: value for key, value in {{cookiecutter}}.items() if not key.startswith("_")}
    filename = Path.cwd() / "cookiecutter-answers.json"
    with filename.open(mode="w") as fobj:
        json.dump({"cookiecutter": answers}, fobj, indent=2)
    print(f"File {filename} saved with all the answers (useful to rebuild with --replay-file).")


def main():
    save_answers()
    validate_redis_implication()


if __name__ == "__main__":
    main()
