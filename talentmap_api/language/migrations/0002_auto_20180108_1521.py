# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-01-08 15:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('language', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='language',
            name='effective_date',
            field=models.DateTimeField(help_text='The date after which the language is in effect'),
        ),
    ]
