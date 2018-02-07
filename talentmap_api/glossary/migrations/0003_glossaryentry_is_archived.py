# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-02-07 15:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('glossary', '0002_auto_20180206_1836'),
    ]

    operations = [
        migrations.AddField(
            model_name='glossaryentry',
            name='is_archived',
            field=models.BooleanField(default=False, help_text='Denotes if this glossary item is archived'),
        ),
    ]