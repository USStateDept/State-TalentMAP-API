# Generated by Django 2.0.4 on 2019-09-19 21:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('position', '0031_merge_20190917_1351'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='assignment',
            name='position',
        ),
        migrations.RemoveField(
            model_name='assignment',
            name='tour_of_duty',
        ),
        migrations.RemoveField(
            model_name='assignment',
            name='user',
        ),
        migrations.RemoveField(
            model_name='position',
            name='current_assignment',
        ),
        migrations.DeleteModel(
            name='Assignment',
        ),
    ]
