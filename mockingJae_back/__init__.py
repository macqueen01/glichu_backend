from .celery import app as celery_app
# Check the version of ipfs first
# assure ipfs == v0.6.0 and ipfshttpslient == v0.6.0
import ipfshttpclient

client = ipfshttpclient.connect()

__all__ = ('celery_app',)