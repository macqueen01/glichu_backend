# Generated by Django 4.1.5 on 2023-06-06 07:55

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_remix_liked_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='reported_by',
            field=models.ManyToManyField(related_name='reported', to=settings.AUTH_USER_MODEL),
        ),
    ]
