# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-02-12 14:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('position', '0009_historicalcapsuledescription'),
    ]

    operations = [
        migrations.AlterField(
            model_name='skillcone',
            name='_skill_codes',
            field=models.TextField(blank=True, default='', null=True),
        ),
    ]
