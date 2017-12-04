from django.db.models import F, Sum, Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models
from django.contrib.auth.models import User

from dateutil.relativedelta import relativedelta

from django.contrib.postgres.fields import JSONField

from talentmap_api.common.common_helpers import get_filtered_queryset, resolve_path_to_view, month_diff
from talentmap_api.common.decorators import respect_instance_signalling

from talentmap_api.messaging.models import Notification


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    date_of_birth = models.DateField(null=True)
    mandatory_retirement_date = models.DateField(null=True)
    phone_number = models.TextField(null=True)

    cdo = models.ForeignKey('self', related_name='direct_reports', null=True)

    language_qualifications = models.ManyToManyField('language.Qualification', related_name='qualified_users')

    skill_code = models.ForeignKey('position.Skill', null=True)

    grade = models.ForeignKey('position.Grade', null=True)

    favorite_positions = models.ManyToManyField('position.Position', related_name='favorited_by_users', help_text="Positions which this user has designated as a favorite")

    primary_nationality = models.ForeignKey('organization.Country', null=True, related_name='primary_citizens', help_text="The user's primary country of citizenship")
    secondary_nationality = models.ForeignKey('organization.Country', null=True, related_name='secondary_citizens', help_text="The user's secondary country of citizenship")

    def __str__(self):
        return f"{self.user.username}"

    def save(self, *args, **kwargs):
        # Set the retirement date to the user's birthdate + 65 years
        if self.date_of_birth:
            self.mandatory_retirement_date = self.date_of_birth + relativedelta(years=65)
        super(UserProfile, self).save(*args, **kwargs)

    @property
    def is_cdo(self):
        '''
        Represents if the user is a CDO (Career development officer) or not. If the user's direct_report
        reverse relationship has any members, they are a CDO
        '''

        return self.direct_reports.count() != 0

    @property
    def is_fairshare(self):
        '''
        Determines if this user is classified as a Fair Share bidder. The rules to calculate this have some
        exceptions, but at this moment only the baseline logic is implemented in the system.
        '''
        # An employee is considered a "Fair Share" bidder if either of the following states are TRUE
        #  - Served at least 20 months at a post with combined differential (diff + danger pay) of >=20
        #  - Served at least 10 months at a post with 1 year standard TOD

        # Get the user's assignment history
        assignments = self.assignments.all()  # This gives us a copy of the queryset we can tinker with

        # Annotate our assignments with the pertinent data
        assignments = assignments.annotate(combined_differential=Sum(F('position__post__differential_rate') + F('position__post__danger_pay')),
                                           standard_tod_months=F('position__post__tour_of_duty__months'))

        # Create our cases
        case_1 = Q(combined_differential__gte=20)
        case_2 = Q(standard_tod_months=12)

        # Filter our assignments to only those matching these cases
        case_1_assignments = assignments.filter(case_1)
        case_2_assignments = assignments.filter(case_2)

        # Calculate the number of months spent in each of these cases
        case_1_lengths = [month_diff(a.start_date, a.end_date) for a in case_1_assignments if a.end_date]
        case_2_lengths = [month_diff(a.start_date, a.end_date) for a in case_2_assignments if a.end_date]

        # Sum our values
        case_1 = sum(case_1_lengths) >= 20
        case_2 = sum(case_2_lengths) >= 10

        # Return true if either are true
        return (case_1 or case_2)

    class Meta:
        managed = True
        ordering = ['user__last_name']


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

    def get_queryset(self):
        return get_filtered_queryset(resolve_path_to_view(self.endpoint).filter_class, self.filters)

    def update_count(self, created=False):
        count = self.get_queryset().count()
        if self.count != count and not created:
            # Create a notification for this saved search's owner if the amount has increased
            diff = count - self.count
            if diff > 0:
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
    instance.update_count(created)
