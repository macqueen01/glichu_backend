# Generated by Django 4.1.5 on 2023-05-15 04:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0021_remix_uploaded_to_s3'),
    ]

    operations = [
        migrations.AddField(
            model_name='remix',
            name='task_queue_json',
            field=models.TextField(default='{}', null=True),
        ),
    ]
