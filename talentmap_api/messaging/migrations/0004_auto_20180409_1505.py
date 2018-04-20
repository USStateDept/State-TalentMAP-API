# Generated by Django 2.0.4 on 2018-04-09 15:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('messaging', '0003_task'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sharable',
            name='receiving_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='received_shares', to='user_profile.UserProfile'),
        ),
        migrations.AlterField(
            model_name='sharable',
            name='sharing_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='sent_shares', to='user_profile.UserProfile'),
        ),
    ]