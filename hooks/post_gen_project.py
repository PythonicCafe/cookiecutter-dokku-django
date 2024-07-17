import os


if "{{ cookiecutter.enable_celery }}".lower() != "y":
    os.remove("project/celery.py")
    os.remove("bin/worker.sh")

if "{{ cookiecutter.enable_redis }}".lower() != "y":
    os.remove("docker/env/messaging")

if "{{ cookiecutter.enable_mailhog }}".lower() != "y":
    os.remove("docker/env/mail")

if "{{ cookiecutter.enable_minio }}".lower() != "y":
    os.remove("docker/env/storage")

if "{{ cookiecutter.database_software }}".lower() != "postgres":
    os.remove(".psqlrc")
