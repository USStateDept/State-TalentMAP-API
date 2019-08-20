from django.db import models

from talentmap_api.common.models import StaticRepresentationModel

# Create your models here.


class LoginInstance(StaticRepresentationModel):
    user = models.ForeignKey('user_profile.UserProfile', on_delete=models.CASCADE, help_text="The user logging in")
    date_of_login = models.DateTimeField(null=True)

    class Meta:
        managed = True
        ordering = ['id']
