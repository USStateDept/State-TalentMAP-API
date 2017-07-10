# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-29 21:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('language', '0004_auto_20170629_2116'),
    ]

    operations = [
        migrations.AlterField(
            model_name='language',
            name='code',
            field=models.TextField(db_index=True, help_text='The code representation of the language', unique=True),
        ),
        migrations.AlterField(
            model_name='proficiency',
            name='code',
            field=models.TextField(help_text='The code representing the linguistic proficiency', unique=True),
        ),
    ]
