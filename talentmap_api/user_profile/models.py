from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models
from django.contrib.auth.models import User

from django.contrib.postgres.fields import JSONField


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    language_qualifications = models.ManyToManyField('language.Qualification', related_name='qualified_users')

    favorite_positions = models.ManyToManyField('position.Position', related_name='favorited_by_users', help_text="Positions which this user has designated as a favorite")

    def __str__(self):
        return f"{self.user.username}"


class Sharable(models.Model):
    '''
    This model represents a shared item from one user to another. The field sharable_model
    is the string representation of the model, for example 'position.Position', and the
    sharable_id is the integer representation of the autofield primary key for that model
    '''
    sharing_user = models.ForeignKey(UserProfile, related_name="sent_shares")
    receiving_user = models.ForeignKey(UserProfile, related_name="received_shares")

    # Sharable
    sharable_id = models.IntegerField(help_text="The ID of the model instance for this sharable")
    sharable_model = models.TextField(help_text="The string of the model")

    read = models.BooleanField(default=False, help_text="Whether this sharable has been read")

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        ordering = ["date_created"]


class SavedSearch(models.Model):
    '''
    Represents a saved search.
    '''
    owner = models.ForeignKey(UserProfile, related_name="saved_searches")

    name = models.TextField(default="Saved Search", help_text="The name of the saved search")
    endpoint = models.TextField(help_text="The endpoint for this search and filter")

    '''
    Filters should be a JSON object of filters representing a search. Generally, the values
    should be stored in a list.
    For example, suppose our user preferred posts with post danger pay >= 20 and with grade = 05

    {
       "post__danger_pay__gte": ["20"],
       "grade__code": ["05"]
    }
    '''
    filters = JSONField(default=dict, help_text="JSON object containing filters representing the saved search")

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        ordering = ["date_created"]


# Signal listeners
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    '''
    This listener creates a user profile for every created user.
    '''
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=Sharable)
def email_notification(sender, instance, created, **kwargs):
    '''
    This listener e-mails the receiving user to notify them of their share.
    '''
    if created:
        # TODO: Add e-mail here when e-mail implementation is determined
        pass
