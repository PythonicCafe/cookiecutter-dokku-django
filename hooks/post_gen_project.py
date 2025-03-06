import os
import shutil


if "{{ cookiecutter.enable_celery }}".lower() != "y":
    os.remove("project/celery.py")
    os.remove("project/utils/celery.py")
    os.remove("bin/worker.sh")

if "{{ cookiecutter.enable_redis }}".lower() != "y":
    os.remove("docker/env/messaging")
    shutil.rmtree("docker/data/messaging")

if "{{ cookiecutter.enable_mailhog }}".lower() != "y":
    os.remove("docker/env/mail")
    shutil.rmtree("docker/data/mail")

if "{{ cookiecutter.enable_minio }}".lower() != "y":
    os.remove("docker/env/storage")
    shutil.rmtree("docker/data/storage")

if "{{ cookiecutter.database_software }}".lower() != "postgres":
    os.remove(".psqlrc")
    os.remove("docker/conf/db/postgresql.dev.conf")
    os.remove("docker/conf/db/postgresql.prd.conf")
elif "{{ cookiecutter.database_software }}".lower() != "mariadb":
    os.remove("docker/conf/db/my.cnf")


if "{{ cookiecutter.postgres_fts_utils }}".lower() != "y":
    os.remove("project/utils/search.py")
