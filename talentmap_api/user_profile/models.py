from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models
from django.contrib.auth.models import User

from django.contrib.postgres.fields import JSONField

from talentmap_api.common.common_helpers import get_filtered_queryset, resolve_path_to_view
from talentmap_api.common.decorators import respect_instance_signalling

from talentmap_api.messaging.models import Notification


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    cdo = models.ForeignKey('self', related_name='direct_reports', null=True)

    language_qualifications = models.ManyToManyField('language.Qualification', related_name='qualified_users')

    skill_code = models.ForeignKey('position.Skill', null=True)

    grade = models.ForeignKey('position.Grade', null=True)

    favorite_positions = models.ManyToManyField('position.Position', related_name='favorited_by_users', help_text="Positions which this user has designated as a favorite")

    def __str__(self):
        return f"{self.user.username}"


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

    count = models.IntegerField(default=0, help_text="Current count of search results for this search")

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def update_count(self):
        count = get_filtered_queryset(resolve_path_to_view(self.endpoint).filter_class, self.filters).count()
        if self.count != count:
            # Create a notification for this saved search's owner if the amount has increased
            diff = count - self.count
            if diff > 0:
                Notification.objects.create(
                    owner=self.owner,
                    message=f"Saved search {self.name} has {diff} new results available"
                )

            self.count = count

            # Do not trigger signals for this save
            self._disable_signals = True
            self.save()
            self._disable_signals = False

    @staticmethod
    def update_counts_for_endpoint(endpoint=None):
        '''
        Update all saved searches counts whose endpoint matches the specified endpoint.
        If the endpoint is omitted, updates all saved search counts.

        Args:
            - endpoint (string) - Endpoint to updated saved searches for
        '''

        queryset = SavedSearch.objects.all()
        if endpoint:
            queryset = SavedSearch.objects.filter(endpoint=endpoint)

        for search in queryset:
            search.update_count()

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


@receiver(post_save, sender=SavedSearch)
@respect_instance_signalling()
def post_saved_search_save(sender, instance, created, **kwargs):
    '''
    This listener ensures newly created or edited saved searches update their counts
    '''
    instance.update_count()
