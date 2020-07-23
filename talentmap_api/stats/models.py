from django.db import models
from django.contrib.postgres.fields import JSONField


class LoginInstance(models.Model):
    user = models.ForeignKey('user_profile.UserProfile', on_delete=models.CASCADE, help_text="The user logging in")
    date_of_login = models.DateTimeField(null=True)
    details = JSONField(default=dict, help_text="JSON object containing browser browser information")

    class Meta:
        managed = True
        ordering = ['id']
