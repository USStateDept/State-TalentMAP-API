# Generated by Django 2.0.4 on 2019-09-16 18:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('messaging', '0004_auto_20180409_1505'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notification',
            name='_string_representation',
        ),
        migrations.RemoveField(
            model_name='sharable',
            name='_string_representation',
        ),
        migrations.RemoveField(
            model_name='task',
            name='_string_representation',
        ),
    ]