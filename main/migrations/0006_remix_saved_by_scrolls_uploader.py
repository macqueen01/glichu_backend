# Generated by Django 4.1.5 on 2023-06-06 11:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_user_reported_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='remix',
            name='saved_by_scrolls_uploader',
            field=models.IntegerField(default=0),
        ),
    ]
