from django.db.models import F, Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models
from django.contrib.auth.models import User

from dateutil.relativedelta import relativedelta

from django.contrib.postgres.fields import JSONField

from talentmap_api.common.models import StaticRepresentationModel
from talentmap_api.common.common_helpers import get_filtered_queryset, resolve_path_to_view, ensure_date, format_filter
from talentmap_api.common.decorators import respect_instance_signalling

from talentmap_api.messaging.models import Notification


class UserProfile(StaticRepresentationModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    date_of_birth = models.DateTimeField(null=True)
    mandatory_retirement_date = models.DateTimeField(null=True)
    phone_number = models.TextField(null=True)

    cdo = models.ForeignKey('self', on_delete=models.DO_NOTHING, related_name='direct_reports', null=True)

    language_qualifications = models.ManyToManyField('language.Qualification', related_name='qualified_users')

    skills = models.ManyToManyField('position.Skill')

    grade = models.ForeignKey('position.Grade', on_delete=models.DO_NOTHING, null=True)

    favorite_positions = models.ManyToManyField('bidding.CyclePosition', related_name='favorited_by_users', help_text="Cycle Positions which this user has designated as a favorite")

    primary_nationality = models.ForeignKey('organization.Country', on_delete=models.DO_NOTHING, null=True, related_name='primary_citizens', help_text="The user's primary country of citizenship")
    secondary_nationality = models.ForeignKey('organization.Country', on_delete=models.DO_NOTHING, null=True, related_name='secondary_citizens', help_text="The user's secondary country of citizenship")

    emp_id = models.TextField(null=False, help_text="The user's employee id")

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

    def save(self, *args, **kwargs):
        # Set the retirement date to the user's birthdate + 65 years
        if self.date_of_birth:
            self.mandatory_retirement_date = ensure_date(self.date_of_birth) + relativedelta(years=65)
        super(UserProfile, self).save(*args, **kwargs)

    @property
    def display_name(self):
        '''
        Returns the user's display name, derived from first name, username or e-mail
        '''
        display_name = ""
        if self.user.first_name:
            display_name = self.user.first_name
        elif self.user.username:
            display_name = self.user.username
        else:
            display_name = self.user.email

        return display_name

    @property
    def initials(self):
        '''
        Returns the user's initials, derived from first name/last name or e-mail
        '''
        initials = ""
        if self.user.first_name and self.user.last_name:
            initials = f"{self.user.first_name[0]}{self.user.last_name[0]}"
        if len(initials) == 0:
            # No first name/last name on user object, derive from email
            # Example email: StateJB@state.gov
            # [x for x in self.user.email if x.isupper()] - get all capitals
            # [:2] - get the first two
            # [::-1] - reverse the list
            initials = "".join([x for x in self.user.email if x.isupper()][:2][::-1])

        return initials

    @property
    def is_cdo(self):
        '''
        Represents if the user is a CDO (Career development officer) or not. If the user's direct_report
        reverse relationship has any members, they are a CDO
        '''

        return self.direct_reports.count() != 0

    class Meta:
        managed = True
        ordering = ['user__last_name']


class SavedSearch(models.Model):
    '''
    Represents a saved search.
    '''
    owner = models.ForeignKey(UserProfile, on_delete=models.DO_NOTHING, related_name="saved_searches")

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

    def get_queryset(self):
        return get_filtered_queryset(resolve_path_to_view(self.endpoint).filter_class, self.filters)

    def update_count(self, created=False, jwt_token=''):

        filter_class = resolve_path_to_view(self.endpoint).filter_class
        query_params = format_filter(self.filters)
        if getattr(filter_class, "use_api", False):
            count = filter_class.get_count(query_params, jwt_token)['count']
        else:
            count = self.get_queryset().count()


        if self.count != count:
            # Create a notification for this saved search's owner if the amount has increased
            diff = count - self.count
            if diff > 0 and not created:
                Notification.objects.create(
                    owner=self.owner,
                    tags=['saved_search'],
                    message=f"Saved search {self.name} has {diff} new results available"
                )

            self.count = count

            # Do not trigger signals for this save
            self._disable_signals = True
            self.save()
            self._disable_signals = False

    @staticmethod
    def update_counts_for_endpoint(endpoint=None, contains=False, jwt_token='', user=''):
        '''
        Update all saved searches counts whose endpoint matches the specified endpoint.
        If the endpoint is omitted, updates all saved search counts.

        Args:
            - endpoint (string) - Endpoint to updated saved searches for
        '''

        queryset = SavedSearch.objects.all()
        if endpoint:
            if contains:
                queryset = SavedSearch.objects.filter(endpoint__icontains=endpoint)
            else:
                queryset = SavedSearch.objects.filter(endpoint=endpoint)

        for search in queryset:
            if search.owner == user or user == '':
                search.update_count(jwt_token=jwt_token)

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
