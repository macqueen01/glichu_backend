from .celery import app as celery_app
import ipfshttpclient

client = ipfshttpclient.connect()

__all__ = ('celery_app',)