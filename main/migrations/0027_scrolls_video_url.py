# Generated by Django 4.1.4 on 2023-05-21 07:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0026_alter_user_profile_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='scrolls',
            name='video_url',
            field=models.CharField(default='/', max_length=400),
        ),
    ]