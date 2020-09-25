from django.db import models
from jsonfield import JSONField


class LoginInstance(models.Model):
    user = models.ForeignKey('user_profile.UserProfile', on_delete=models.CASCADE, help_text="The user logging in")
    date_of_login = models.DateTimeField(null=True)
    details = JSONField(default=dict, help_text="JSON object containing browser browser information")

    class Meta:
        managed = True
        ordering = ['id']

class ViewPositionInstance(models.Model):
    user = models.ForeignKey('user_profile.UserProfile', on_delete=models.CASCADE, help_text="The user viewing the position")
    position_id = models.TextField(null=False)
    position_type = models.CharField(max_length=3, default='AP', null=False)
    date_of_view = models.DateTimeField(null=False)
    date_of_view_day = models.TextField(null=False)
    date_of_view_week = models.TextField(null=False)

    class Meta:
        managed = True
        ordering = ['id']
