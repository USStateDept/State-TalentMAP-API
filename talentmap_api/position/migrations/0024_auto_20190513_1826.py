# Generated by Django 2.0.4 on 2019-05-13 18:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('position', '0023_positionbidstatistics_has_handshake_accepted'),
    ]

    operations = [
        migrations.AddField(
            model_name='positionbidstatistics',
            name='is_hard_to_fill',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='positionbidstatistics',
            name='is_urgent_vacancy',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='positionbidstatistics',
            name='is_volunteer',
            field=models.BooleanField(default=False),
        ),
    ]