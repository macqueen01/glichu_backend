# Generated by Django 4.1.5 on 2023-05-11 11:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0015_remove_user_name_user_apple_id_user_instagram_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='apple_username',
            field=models.CharField(blank=True, max_length=120, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='instagram_username',
            field=models.CharField(blank=True, max_length=120, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='apple_id',
            field=models.CharField(blank=True, max_length=120, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='instagram_id',
            field=models.CharField(blank=True, max_length=120, null=True, unique=True),
        ),
    ]
