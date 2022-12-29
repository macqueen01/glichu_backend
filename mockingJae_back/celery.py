import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mockingJae_back.settings')

app = Celery(
    'mockingJae_back',
    broker='redis://localhost:6379',
    backend='rpc://',
    include=['mockingJae_back.tasks']
    )

app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.update(result_expires=3600)
app.autodiscover_tasks()

if __name__ == '__main__':
    app.start()

