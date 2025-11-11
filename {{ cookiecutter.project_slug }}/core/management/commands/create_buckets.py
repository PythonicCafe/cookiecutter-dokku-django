from django.conf import settings
from django.core.management.base import BaseCommand

from project.storage import storage


class Command(BaseCommand):
    help = "Create base buckets"

    def handle(self, *args, **kwargs):
        buckets = storage.buckets()
        if settings.AWS_STORAGE_BUCKET_NAME not in buckets:
            storage.create_bucket(settings.AWS_STORAGE_BUCKET_NAME)
