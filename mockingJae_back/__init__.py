from .celery import app as celery_app
# Check the version of ipfs first
# assure ipfs == v0.6.0 and ipfshttpslient == v0.6.0
import ipfshttpclient


try:
    client = ipfshttpclient.connect()
except:
    print('running ipfs add directly')

__all__ = ('celery_app',)

