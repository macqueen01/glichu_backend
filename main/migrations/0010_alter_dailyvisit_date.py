# Generated by Django 4.1.5 on 2023-06-14 16:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_dailyvisit'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dailyvisit',
            name='date',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
