from django.apps import apps


REMIX_MODEL = apps.get_model(
            app_label='main', model_name='Remix', require_ready=True)
SCROLLS_MODEL = apps.get_model(
        app_label='main', model_name='Scrolls', require_ready=True)
MEDIA_MODEL = apps.get_model(
            app_label='main', model_name='VideoMedia', require_ready=True)