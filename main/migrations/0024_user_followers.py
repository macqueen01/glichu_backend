# Generated by Django 4.1.5 on 2023-05-19 05:48

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0023_remixpermission'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='followers',
            field=models.ManyToManyField(related_name='followings', to=settings.AUTH_USER_MODEL),
        ),
    ]