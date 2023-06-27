from django.db import models
from jsonfield import JSONField


class Notification(models.Model):
    '''
    This model represents an individual notification item
    '''

    message = models.TextField(help_text="The message for the notification")
    owner = models.ForeignKey('user_profile.UserProfile', on_delete=models.CASCADE, null=False, related_name="notifications", help_text="The owner of the notification")
    tags = JSONField(default=[], help_text="Tags to categorize the notification")
    meta = models.TextField(default='{}', help_text="Meta data about the notification") # Has to be TextField due to ORA-01754

    is_read = models.BooleanField(default=False, help_text="Whether this notification has been read")

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        ordering = ["date_updated"]
