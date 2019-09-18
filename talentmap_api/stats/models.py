from django.db import models

class LoginInstance(models.Model):
    user = models.ForeignKey('user_profile.UserProfile', on_delete=models.CASCADE, help_text="The user logging in")
    date_of_login = models.DateTimeField(null=True)

    class Meta:
        managed = True
        ordering = ['id']
