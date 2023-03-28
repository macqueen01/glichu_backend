import boto3
import os
from rest_framework.settings import api_settings
from storages.backends.s3boto3 import S3Boto3Storage
from django.core.files.storage import FileSystemStorage


class LocalStorage(FileSystemStorage):
    def __init__(self, location=None, base_url=None, file_permissions_mode=None, directory_permissions_mode=None):
        super().__init__(location=location, base_url=base_url, file_permissions_mode=file_permissions_mode, directory_permissions_mode=directory_permissions_mode)

class S3Storage(S3Boto3Storage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)