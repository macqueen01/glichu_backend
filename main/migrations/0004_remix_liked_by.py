# Generated by Django 4.1.5 on 2023-06-05 16:52

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_remix_reported_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='remix',
            name='liked_by',
            field=models.ManyToManyField(null=True, related_name='liked_remixes', to=settings.AUTH_USER_MODEL),
        ),
    ]
