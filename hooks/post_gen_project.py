import json
import os
import shutil
from pathlib import Path


def post_db_config():
    if "{{ cookiecutter.database_software }}".lower() != "postgres":
        os.remove(".psqlrc")
        os.remove("docker/conf/db/postgresql.dev.conf")
        os.remove("docker/conf/db/postgresql.prd.conf")
    elif "{{ cookiecutter.database_software }}".lower() != "mariadb":
        os.remove("docker/conf/db/my.cnf")


def post_postgres_fts_config():
    if "{{ cookiecutter.postgres_fts_utils }}".lower() != "y":
        os.remove("project/utils/search.py")


def post_celery_config():
    if "{{ cookiecutter.enable_celery }}".lower() != "y":
        os.remove("project/celery.py")
        os.remove("project/utils/celery.py")
        os.remove("bin/worker.sh")


def post_redis_config():
    if "{{ cookiecutter.enable_redis }}".lower() != "y":
        os.remove("docker/env/messaging")
        shutil.rmtree("docker/data/messaging")


def post_mailhog_config():
    if "{{ cookiecutter.enable_mailhog }}".lower() != "y":
        os.remove("docker/env/mail")
        shutil.rmtree("docker/data/mail")


def post_minio_config():
    if "{{ cookiecutter.enable_minio }}".lower() != "y":
        os.remove("docker/env/storage")
        os.remove("core/management/commands/create_buckets.py")
        shutil.rmtree("docker/data/storage")


def post_dokku_config():
    # Create `app.json`
    with open("app.json", mode="r") as fobj:
        app_json = json.load(fobj)

    if "cron" not in app_json:
        app_json["cron"] = []
    if "{{ cookiecutter.enable_mailhog }}".lower() == "y":
        app_json["cron"].extend(
            [
                {"schedule": "2-59/5  *        * * *", "command": "python manage.py retry_deferred"},
                {"schedule": "23      0        * * *", "command": "python manage.py purge_mail_log 180"},
            ]
        )
    else:
        os.remove("bin/mail-worker.sh")
    with open("app.json", mode="w") as fobj:
        json.dump(app_json, fobj, indent=2)


def print_finish():
    print(f"Project generated on {Path.cwd()}")

def main():
    post_db_config()
    post_postgres_fts_config()
    post_celery_config()
    post_redis_config()
    post_mailhog_config()
    post_minio_config()
    post_dokku_config()
    print_finish()


if __name__ == "__main__":
    main()
