# Generated by Django 2.0.4 on 2019-05-19 13:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bidding', '0012_auto_20190517_2023'),
    ]

    operations = [
        migrations.AddField(
            model_name='cycleposition',
            name='created',
            field=models.DateTimeField(help_text='The created date for the cycle positon', null=True),
        ),
        migrations.AddField(
            model_name='cycleposition',
            name='updated',
            field=models.DateTimeField(help_text='The updated date for the cycle positon', null=True),
        ),
    ]
