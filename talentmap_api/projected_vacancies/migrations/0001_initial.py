# Generated by Django 2.0.4 on 2019-05-07 13:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('user_profile', '0005_userprofile_emp_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectedVacancyFavorite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('_string_representation', models.TextField(blank=True, help_text='The string representation of this object', null=True)),
                ('position_number', models.TextField()),
                ('user', models.ForeignKey(help_text='The user to which this favorite belongs', on_delete=django.db.models.deletion.DO_NOTHING, to='user_profile.UserProfile')),
            ],
            options={
                'ordering': ['position_number'],
                'managed': True,
            },
        ),
        migrations.AlterUniqueTogether(
            name='projectedvacancyfavorite',
            unique_together={('position_number', 'user')},
        ),
    ]