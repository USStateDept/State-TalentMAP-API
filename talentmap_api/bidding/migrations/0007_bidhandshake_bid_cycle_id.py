# Generated by Django 3.2.4 on 2021-08-03 16:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bidding', '0006_bidhandshakecycle'),
    ]

    operations = [
        migrations.AddField(
            model_name='bidhandshake',
            name='bid_cycle_id',
            field=models.IntegerField(help_text='The bid cycle ID', null=True),
        ),
    ]