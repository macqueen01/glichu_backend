# Generated by Django 4.1.5 on 2023-05-17 05:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0022_remix_task_queue_json'),
    ]

    operations = [
        migrations.CreateModel(
            name='RemixPermission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('scrolls_uploader_has_access', models.IntegerField(default=0)),
                ('all_users_have_access', models.IntegerField(default=0)),
                ('remix', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.remix')),
            ],
        ),
    ]
