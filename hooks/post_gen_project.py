import os


if "{{ cookiecutter.enable_celery }}".lower() != "y":
    os.remove("project/celery.py")
    os.remove("bin/worker.sh")

if "{{ cookiecutter.enable_redis }}".lower() != "y":
    os.remove("docker/env/redis")

if "{{ cookiecutter.enable_mailhog }}".lower() != "y":
    os.remove("docker/env/mail")
