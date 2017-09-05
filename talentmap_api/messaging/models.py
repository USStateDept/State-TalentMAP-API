from django.db import models


class Notification(models.Model):
    '''
    This model represents an individual notification item
    '''

    message = models.TextField(null=False, help_text="The message for the notification")
    owner = models.ForeignKey('user_profile.UserProfile', on_delete=models.CASCADE, null=False, related_name="notifications", help_text="The owner of the notification")

    is_read = models.BooleanField(default=False, help_text="Whether this notification has been read")

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        ordering = ["date_updated"]
