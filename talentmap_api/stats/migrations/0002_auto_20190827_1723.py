# Generated by Django 2.0.4 on 2019-08-27 17:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='logininstance',
            options={'managed': True, 'ordering': ['id']},
        ),
    ]