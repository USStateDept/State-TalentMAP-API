from django.db.models import F, Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models
from django.contrib.auth.models import User

from dateutil.relativedelta import relativedelta

from django.contrib.postgres.fields import JSONField

from talentmap_api.common.models import StaticRepresentationModel
from talentmap_api.common.common_helpers import get_filtered_queryset, resolve_path_to_view, ensure_date
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

    favorite_positions = models.ManyToManyField('position.Position', related_name='favorited_by_users', help_text="Positions which this user has designated as a favorite")

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

    @property
    def is_six_eight(self):
        '''
        Determines if this user is classified as a 6/8 valid bidder. The rules to calculate this have some
        exceptions, but this is just a baseline logic implementation for the time being.
        '''
        # An employee is valid under 6/8 rules if the following states are TRUE
        #  - Has served a sufficient portion of a non-domestic tour of duty (10 of 12, 20 of 24, 30 of 36 or 83% of others)
        #    such that there is no contiguous block (have removed invalid non-domestic TOD assignments) of 6 or 8 years domestic service

        # Get the user's assignment history
        assignments = self.assignments.all().filter(status__in=[self.assignments.model.Status.completed, self.assignments.model.Status.curtailed])

        # Annotate with the TOD months to avoid a lookup error
        assignments = assignments.annotate(tod_months=F("tour_of_duty__months")).annotate(required_service=F("tod_months") * 0.83)

        # Create a case to filter for USA positions
        usa_q_obj = Q(is_domestic=True)
        # Create cases for the 12, 24, and 36 month cases
        tod_case_1 = Q(tod_months=12, service_duration__gte=10)
        tod_case_2 = Q(tod_months=24, service_duration__gte=20)
        tod_case_3 = Q(tod_months=36, service_duration__gte=30)
        # Create case for the Non 12, 24, and 36 month cases
        tod_case_4 = ~Q(tod_months__in=[12, 24, 36]) & Q(service_duration__gte=F("required_service"))
        tod_cases = tod_case_1 | tod_case_2 | tod_case_3 | tod_case_4

        valid_case = usa_q_obj | (~usa_q_obj & tod_cases)

        # Keep only assignments which are domestic, and foreign assignments which meet the criteria
        assignments = assignments.filter(valid_case).order_by("-start_date")

        # Count our assignments in order from most recent to oldest, counting the service duration until we
        # hit a foreign assignment, which is now guaranteed to be a valid duration to break apart 6/8 tabulations
        total = 0
        for assignment in list(assignments):
            if not assignment.is_domestic:
                break
            total += assignment.service_duration

        # If the total number of now contiguous domestic service exceeds 6 years we should return FALSE as we don't meet the requirements
        return total < (6 * 12)

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
        assignments = self.assignments.all().filter(status__in=[self.assignments.model.Status.completed, self.assignments.model.Status.curtailed])

        # Create our cases
        case_1 = Q(combined_differential__gte=20) | Q(combined_differential__gte=15, bid_approval_date__lte="2017-06-30T23:59:59Z")
        case_2 = Q(standard_tod_months=12)

        # Filter our assignments to only those matching these cases
        case_1_assignments = assignments.filter(case_1)
        case_2_assignments = assignments.filter(case_2)

        # Calculate the number of months spent in each of these cases
        case_1_lengths = case_1_assignments.values_list("service_duration", flat=True)
        case_2_lengths = case_2_assignments.values_list("service_duration", flat=True)

        # Sum our values
        case_1 = sum(case_1_lengths) >= 20
        case_2 = sum(case_2_lengths) >= 10

        # Return true if either are true
        return (case_1 or case_2)

    class Meta:
        managed = True
        ordering = ['user__last_name']


class SavedSearch(StaticRepresentationModel):
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
    def update_counts_for_endpoint(endpoint=None, contains=False):
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
