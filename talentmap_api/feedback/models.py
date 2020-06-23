from django.db import models


class FeedbackEntry(models.Model):
    """
    Represents an individual feedback item
    """

    comments = models.TextField(null=True, max_length=280)
    user = models.ForeignKey('user_profile.UserProfile', on_delete=models.DO_NOTHING, null=True, help_text="The commenting user, if available")

    is_interested_in_helping = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        ordering = ["-date_created"]
