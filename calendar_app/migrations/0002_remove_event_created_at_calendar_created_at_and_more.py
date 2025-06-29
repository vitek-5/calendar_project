# Generated by Django 5.2.1 on 2025-06-18 11:19

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calendar_app', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='created_at',
        ),
        migrations.AddField(
            model_name='calendar',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='calendar',
            name='name',
            field=models.CharField(default='Unnamed Calendar', max_length=255, verbose_name='Название календаря'),
            preserve_default=False,
        ),
    ]
