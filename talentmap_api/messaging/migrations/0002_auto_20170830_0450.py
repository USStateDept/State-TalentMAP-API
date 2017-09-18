# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-30 04:50
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('messaging', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='owner',
            field=models.ForeignKey(help_text='The owner of the notification', on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='user_profile.UserProfile'),
        ),
    ]