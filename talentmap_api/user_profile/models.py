from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models
from django.contrib.auth.models import User

from django.contrib.postgres.fields import JSONField


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    language_qualifications = models.ManyToManyField('language.Qualification', related_name='qualified_users')

    '''
    Position preferences should be a JSON object of filters representing a user's position preferences.
    For example, suppose our user preferred posts with post danger pay >= 20 and with grade = 05

    {
        "post__danger_pay__gte": 20,
        "grade__code": "05"
    }
    '''
    position_preferences = JSONField(default=dict, help_text="JSON object containing filters representing a user's position preferences")

    favorite_positions = models.ManyToManyField('position.Position', related_name='favorited_by_users', help_text="Positions which this user has designated as a favorite")


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    '''
    This listener creates a user profile for every created user.
    '''
    if created:
        UserProfile.objects.create(user=instance)
