import itertools

from django.db.models import OuterRef, Subquery
from django.db import models
from djchoices import DjangoChoices, ChoiceItem
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from simple_history.models import HistoricalRecords

from dateutil.relativedelta import relativedelta

import talentmap_api.bidding.models
from talentmap_api.common.common_helpers import ensure_date, month_diff, safe_navigation
from talentmap_api.common.models import StaticRepresentationModel
from talentmap_api.organization.models import Organization, Post
from talentmap_api.language.models import Qualification
from talentmap_api.bidding.models import CyclePosition


class Position(StaticRepresentationModel):
    '''
    The position model represents a job by combining different requirements, as
    well as geographic location
    '''

    position_number = models.TextField(null=True, help_text='The position number')
    description = models.OneToOneField('position.CapsuleDescription', on_delete=models.DO_NOTHING, related_name='position', null=True, help_text="A plain text description of the position")
    title = models.TextField(null=True, help_text='The position title')

    # Positions can have any number of language requirements
    languages = models.ManyToManyField('language.Qualification', related_name='positions')

    # Positions most often share their tour of duty with the post, but sometimes vary
    tour_of_duty = models.ForeignKey('organization.TourOfDuty', on_delete=models.DO_NOTHING, related_name='positions', null=True, help_text='The tour of duty of the post')

    # Positions can have any number of classifications
    classifications = models.ManyToManyField('position.Classification', related_name='positions')
    current_assignment = models.ForeignKey('position.Assignment', on_delete=models.DO_NOTHING, null=True, related_name='current_for_position')

    grade = models.ForeignKey('position.Grade', on_delete=models.DO_NOTHING, related_name='positions', null=True, help_text='The job grade for this position')
    skill = models.ForeignKey('position.Skill', on_delete=models.DO_NOTHING, related_name='positions', null=True, help_text='The job skill for this position')

    organization = models.ForeignKey('organization.Organization', on_delete=models.DO_NOTHING, related_name='organization_positions', null=True, help_text='The organization for this position')
    bureau = models.ForeignKey('organization.Organization', on_delete=models.DO_NOTHING, related_name='bureau_positions', null=True, help_text='The bureau for this position')
    post = models.ForeignKey('organization.Post', on_delete=models.DO_NOTHING, related_name='positions', null=True, help_text='The position post')

    is_overseas = models.BooleanField(default=False, help_text="Flag designating whether the position is overseas")
    is_highlighted = models.BooleanField(default=False, help_text="Flag designating whether the position is highlighted by an organization")

    latest_bidcycle = models.ForeignKey('bidding.BidCycle', on_delete=models.DO_NOTHING, related_name='latest_cycle_for_positions', null=True, help_text="The latest bid cycle this position is in")

    history = HistoricalRecords()

    create_date = models.DateTimeField(null=True, help_text="The creation date of the position")
    update_date = models.DateTimeField(null=True, help_text="The update date of this position")
    effective_date = models.DateTimeField(null=True, help_text="The effective date of this position")
    posted_date = models.DateTimeField(null=True, help_text="The posted date of this position")

    # Values from the original XML/DB that are maintained but not displayed
    _seq_num = models.TextField(null=True)
    _title_code = models.TextField(null=True)
    _org_code = models.TextField(null=True)
    _bureau_code = models.TextField(null=True)
    _skill_code = models.TextField(null=True)
    _staff_ptrn_skill_code = models.TextField(null=True)
    _pay_plan_code = models.TextField(null=True)
    _status_code = models.TextField(null=True)
    _service_type_code = models.TextField(null=True)
    _grade_code = models.TextField(null=True)
    _post_code = models.TextField(null=True)
    _language_1_code = models.TextField(null=True)
    _language_2_code = models.TextField(null=True)
    _location_code = models.TextField(null=True)
    # These are not the required languages, those are in language_1_code, etc.
    _language_req_1_code = models.TextField(null=True)
    _language_req_2_code = models.TextField(null=True)
    _language_1_spoken_proficiency_code = models.TextField(null=True)
    _language_1_reading_proficiency_code = models.TextField(null=True)
    _language_2_spoken_proficiency_code = models.TextField(null=True)
    _language_2_reading_proficiency_code = models.TextField(null=True)
    _create_id = models.TextField(null=True)
    _update_id = models.TextField(null=True)
    _jobcode_code = models.TextField(null=True)
    _occ_series_code = models.TextField(null=True)

    @property
    def similar_positions(self):
        '''
        Returns a query set of similar positions, using the base criteria.
        If there are not at least 3 results, the criteria is loosened.
        '''
        base_criteria = {
            "post__location__country__id": safe_navigation(self, "post.location.country.id"),
            "skill__code": safe_navigation(self, "skill.code"),
            "grade__code": safe_navigation(self, "grade.code"),
        }

        q_obj = models.Q(**base_criteria)
        position_ids = talentmap_api.bidding.models.CyclePosition.objects.filter(status_code__in=["HS", "OP"]).values_list("position_id", flat=True)
        all_pos_queryset = Position.objects.filter(id__in=position_ids)
        queryset = all_pos_queryset.filter(q_obj).exclude(id=self.id)

        while queryset.count() < 3:
            del base_criteria[list(base_criteria.keys())[0]]
            q_obj = models.Q(**base_criteria)
            queryset = all_pos_queryset.filter(q_obj).exclude(id=self.id)
        return queryset

    def __str__(self):
        return f"[{self.position_number}] {self.title} ({self.post})"

    @property
    def availability(self):
        '''
        Evaluates if this position can accept new bids in it's latest bidcycle
        '''
        if self.latest_bidcycle:
            available, reason = self.can_accept_new_bids(self.latest_bidcycle)
            return {
                "availability": available,
                "reason": reason,
            }
        else:
            return {
                "availability": False,
                "reason": "This position is not in an available bid cycle",
            }

    def can_accept_new_bids(self, bidcycle):
        '''
        Evaluates if this position can accept new bids for the given bidcycle

        Args:
            - bidcycle (Object) - The Bidcycle object to evaluate if this position can accept a bid

        Returns:
            - Boolean - True if the position can accept new bids for the cycle, otherwise False
            - String - An explanation of why this position is not biddable
        '''
        # Commenting this out for now - we don't appear to be synchronizing this boolean
        # if not bidcycle.active:
        #     # We must be looking at an active bidcycle
        #     return False, "Bid cycle is not open"
        if not bidcycle.positions.filter(id=self.id).exists():
            # We must be in the bidcycle's position list
            return False, "Position not in specified bid cycle"

        # Filter this positions bid by bidcycle and our Q object
        q_obj = talentmap_api.bidding.models.Bid.get_unavailable_status_filter()
        fulfilling_bids = CyclePosition.objects.filter(bidcycle=bidcycle, position=self).values_list('bids').filter(q_obj)
        if fulfilling_bids.exists():
            messages = {
                talentmap_api.bidding.models.Bid.Status.handshake_offered: "This position has an outstanding handshake",
                talentmap_api.bidding.models.Bid.Status.handshake_accepted: "This position has an accepted handshake",
                talentmap_api.bidding.models.Bid.Status.in_panel: "This position is currently due for paneling",
                talentmap_api.bidding.models.Bid.Status.approved: "This position has been filled",
            }
            return False, messages[fulfilling_bids.first().status]

        return True, ""

    def update_relationships(self):
        '''
        Update the position relationships
        '''
        # Update language requirements
        self.languages.clear()
        if self._language_1_code:
            qualification = Qualification.get_or_create_by_codes(self._language_1_code,
                                                                 self._language_1_reading_proficiency_code,
                                                                 self._language_1_spoken_proficiency_code)[0]
            if qualification:
                self.languages.add(qualification)
        if self._language_2_code:
            qualification = Qualification.get_or_create_by_codes(self._language_2_code,
                                                                 self._language_2_reading_proficiency_code,
                                                                 self._language_2_spoken_proficiency_code)[0]
            if qualification:
                self.languages.add(qualification)

        # Update grade
        if self._grade_code:
            self.grade = Grade.objects.filter(code=self._grade_code).first()

        # Update skill
        if self._skill_code:
            self.skill = Skill.objects.filter(code=self._skill_code).first()

        # Update organizations
        if self._org_code:
            self.organization = Organization.objects.filter(code=self._org_code).first()
        if self._bureau_code:
            self.bureau = Organization.objects.filter(code=self._bureau_code).first()

        # Update location
        if self._location_code:
            self.post = Post.objects.filter(_location_code=self._location_code).first()
            # No post exists with specified location code, so create it
            if not self.post:
                self.post = Post.objects.create(_location_code=self._location_code)

        # Update description
        if self._seq_num:
            self.description = CapsuleDescription.objects.filter(_pos_seq_num=self._seq_num).first()

        self.save()

    class Meta:
        managed = True
        ordering = ["position_number"]


class PositionBidStatistics(StaticRepresentationModel):
    '''
    Stores the bid statistics on a per-cycle basis for a position
    '''

    position = models.OneToOneField("bidding.CyclePosition", on_delete=models.CASCADE, related_name="bid_statistics")

    total_bids = models.IntegerField(default=0)
    in_grade = models.IntegerField(default=0)
    at_skill = models.IntegerField(default=0)
    in_grade_at_skill = models.IntegerField(default=0)

    has_handshake_offered = models.BooleanField(default=False)
    has_handshake_accepted = models.BooleanField(default=False)

    def update_statistics(self):
        bidcycle_bids = self.position.bids.filter(bidcycle=self.position.bidcycle)
        self.total_bids = bidcycle_bids.count()
        self.in_grade = bidcycle_bids.filter(user__grade=self.position.position.grade).count()
        self.at_skill = bidcycle_bids.filter(user__skills=self.position.position.skill).count()
        self.in_grade_at_skill = bidcycle_bids.filter(user__grade=self.position.position.grade, user__skills=self.position.position.skill).count()
        self.has_handshake_offered = any(x.status == talentmap_api.bidding.models.Bid.Status.handshake_offered for x in bidcycle_bids)
        self.has_handshake_accepted = any(x.status == talentmap_api.bidding.models.Bid.Status.handshake_accepted for x in bidcycle_bids)
        self.save()

    class Meta:
        managed = True


class CapsuleDescription(StaticRepresentationModel):
    '''
    Represents a capsule description, describing the associated object in plain English
    '''

    content = models.TextField(null=True)
    point_of_contact = models.TextField(null=True)
    website = models.TextField(null=True)

    last_editing_user = models.ForeignKey('user_profile.UserProfile', on_delete=models.DO_NOTHING, related_name='edited_capsule_descriptions', null=True, help_text="The last user to edit this description")
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    history = HistoricalRecords()

    _pos_seq_num = models.TextField(null=True)

    class Meta:
        managed = True
        ordering = ["date_updated"]


class Grade(StaticRepresentationModel):
    '''
    The grade model represents an individual job grade
    '''
    # All valid grade codes, and their ranked order. Using a dict instead of a list
    # to avoid try/catch in the save override when getting ranks
    RANK_ORDERING = {
        "CA": 1,
        "CM": 2,
        "MC": 3,
        "OC": 4,
        "OM": 5,
        "00": 6,
        "01": 7,
        "02": 8,
        "03": 9,
        "04": 10,
        "05": 11,
        "06": 12,
        "07": 13,
        "08": 14,
    }

    code = models.TextField(db_index=True, unique=True, null=False)
    rank = models.IntegerField(null=False, default=0)

    def __str__(self):
        return f"{self.code}"

    def update_relationships(self):
        self.rank = Grade.RANK_ORDERING.get(self.code, 0)
        self.save()

    class Meta:
        managed = True
        ordering = ["rank"]


class Skill(StaticRepresentationModel):
    '''
    The skill model represents an individual job skill
    '''

    code = models.TextField(db_index=True, unique=True, null=False, help_text="4 character string code representation of the job skill")
    cone = models.ForeignKey("position.SkillCone", on_delete=models.DO_NOTHING, related_name="skills", null=True)
    description = models.TextField(null=False, help_text="Text description of the job skill")

    def __str__(self):
        return f"{self.description} ({self.code})"

    class Meta:
        managed = True
        ordering = ["code"]


class SkillCone(StaticRepresentationModel):
    '''
    The skill cone represents a grouping of skills
    '''

    name = models.TextField(db_index=True, null=False, help_text="The name of the skill cone")

    # Data as loaded from XML
    _id = models.TextField(null=True)
    _skill_codes = models.TextField(null=True, blank=True, default="")

    @property
    def skill_codes(self):
        '''
        Returns the string list of skill codes as an array
        '''
        return self._skill_codes.split(',')

    @skill_codes.setter
    def skill_codes(self, value):
        '''
        Sets the skill code string to the joined array value
        '''
        if not value:
            value = [""]
        self._skill_codes = ','.join(value)

    def update_relationships(self):
        # Get all other skill cones with the same _id
        same_cone = SkillCone.objects.filter(_id=self._id).exclude(id=self.id)
        skill_codes = self.skill_codes

        if same_cone.count() > 0:
            # Add their skill codes to our skill code list
            new_codes = [x.skill_codes for x in list(same_cone)]
            if len(new_codes) > 0:
                # Use chain to flatten the list of lists
                skill_codes += list(itertools.chain.from_iterable(new_codes))
                # Eliminate duplicates
                skill_codes = list(set(skill_codes))
                # Set the data
                self.skill_codes = skill_codes
                # Save this cone
                self.save()

        # Update all skills to point to this cone
        Skill.objects.filter(code__in=skill_codes).update(cone=self)

        # Delete the duplicate cones
        same_cone.delete()

    def __str__(self):
        return f"{self.name}"

    class Meta:
        managed = True
        ordering = ["name"]


class Classification(StaticRepresentationModel):
    '''
    The position classification model represents a position's classification.
    Maintained as a separate model to support limiting visibility.
    '''

    code = models.TextField(db_index=True, unique=True, null=False, help_text="The classification code")
    description = models.TextField(null=False, help_text="Text description of the classification")

    def __str__(self):
        return f"{self.description} ({self.code})"

    class Meta:
        managed = True
        ordering = ["code"]


class Assignment(StaticRepresentationModel):
    '''
    The assignment model represents a current or past assignment, linking together
    users, positions, tours of duty, and other assignment related data
    '''

    class Status(DjangoChoices):
        pending = ChoiceItem("pending")
        assigned = ChoiceItem("assigned")
        active = ChoiceItem("active")
        completed = ChoiceItem("completed")
        curtailed = ChoiceItem("curtailed")

    class CurtailmentReason(DjangoChoices):
        medical = ChoiceItem("medical")
        clearance = ChoiceItem("clearance")
        service_need = ChoiceItem("service_need", "service_need")
        compassionate = ChoiceItem("compassionate")
        other = ChoiceItem("other")

    # Statuses
    status = models.TextField(default=Status.pending, choices=Status.choices)
    curtailment_reason = models.TextField(null=True, choices=CurtailmentReason.choices)

    # Incumbent and position information
    user = models.ForeignKey('user_profile.UserProfile', on_delete=models.DO_NOTHING, null=True, related_name='assignments')
    position = models.ForeignKey('position.Position', on_delete=models.CASCADE, related_name='assignments')
    tour_of_duty = models.ForeignKey('organization.TourOfDuty', on_delete=models.DO_NOTHING, null=True, related_name='assignments')

    # Chronology information
    create_date = models.DateTimeField(auto_now_add=True, help_text='The date the assignment was created')
    start_date = models.DateTimeField(null=True, help_text='The date the assignment started')
    estimated_end_date = models.DateTimeField(null=True, help_text='The estimated end date based upon tour of duty')
    end_date = models.DateTimeField(null=True, help_text='The date this position was completed or curtailed')
    bid_approval_date = models.DateTimeField(null=True, help_text='The date the bid for this assignment was approved')
    arrival_date = models.DateTimeField(null=True, help_text='The date the incumbent arrived at the position')
    service_duration = models.IntegerField(null=True, help_text='The duration of a completed assignment in months')
    update_date = models.DateTimeField(auto_now=True)

    # Fairshare and 6/8 calculation values
    is_domestic = models.BooleanField(default=False, help_text='Indicates if this position is domestic')
    # The combined differential is calculated according to rules that make it the most beneficial to the bidder
    combined_differential = models.IntegerField(default=0, help_text='The combined differential (danger pay and differential) for this assignment')
    standard_tod_months = models.IntegerField(default=0, help_text='The standard tour of duty for the post at assignment creation')

    @property
    def emp_id(self):
        return self.user.emp_id

    @staticmethod
    def create_from_bid(bid):
        '''
        Creates an assignment from a specified bid
        '''
        if bid.status != talentmap_api.bidding.models.Bid.Status.approved:
            raise Exception("Only an approved bid may create an assignment.")

        assignment = Assignment.objects.create(status=Assignment.Status.assigned,
                                               user=bid.user,
                                               position=bid.position.position,
                                               tour_of_duty=bid.position.position.post.tour_of_duty,
                                               bid_approval_date=bid.approved_date)

        return assignment

    def __str__(self):
        return f"({self.status}) {self.user} at {self.position}"

    class Meta:
        managed = True
        ordering = ["update_date"]


# Signal listeners
@receiver(pre_save, sender=Assignment, dispatch_uid="assignment_pre_save")
def assignment_pre_save(sender, instance, **kwargs):
    '''
    This listener performs operations during the pre-save cylce of the assignment.
    '''

    if not instance.id:
        # This is a new instance
        # Set the domestic flag
        instance.is_domestic = not instance.position.is_overseas
        if safe_navigation(instance, "position.post.tour_of_duty.months"):
            instance.standard_tod_months = instance.position.post.tour_of_duty.months
    else:
        # Get our assignment as it is in the database
        db_assignment = Assignment.objects.get(id=instance.id)

        # Check if our status has changed, and if we're now completed or curtailed
        if instance.status in [Assignment.Status.completed, Assignment.Status.curtailed]:
            # Set our service duration now that the assignment is complete
            if instance.start_date and instance.end_date:
                instance.service_duration = month_diff(ensure_date(instance.start_date), ensure_date(instance.end_date))

            # Set our combined differential according to rules as designated in the SOP
            today = timezone.now()

            sd = ensure_date(instance.start_date)           # Start date
            bd = ensure_date(instance.bid_approval_date)    # Bid date

            sd_post = instance.position.post                # post as of start date
            bd_post = instance.position.post                # post as of bid date

            # If a historical record exists for the post for Nov. 1st, use that
            if sd.year < today.year or \
               (sd.year == today.year and sd.month < 11 and today.month > 11):
                sd_post = sd_post.history.as_of(f"{sd.year}-11-01T00:00:00Z")

            if bd and (bd.year < today.year or (bd.year == today.year and bd.month < 11 and today.month > 11)):
                bd_post = bd_post.history.as_of(f"{bd.year}-11-01T00:00:00Z")

            instance.combined_differential = max((sd_post.differential_rate + sd_post.danger_pay),
                                                 (bd_post.differential_rate + bd_post.danger_pay))

    # Update our estimated end date
    # Set the estimated end date to the date in the future based on tour of duty months
    if instance.start_date and instance.tour_of_duty:
        instance.estimated_end_date = ensure_date(instance.start_date) + relativedelta(months=instance.tour_of_duty.months)


@receiver(post_save, sender=Assignment, dispatch_uid="assignment_post_save")
def assignment_post_save(sender, instance, created, **kwargs):
    '''
    This listener updates all positions' current assignments when any assignment is updated
    '''
    # Update the current assignment for all positions
    latest_assignment = Assignment.objects.filter(position=OuterRef('pk')).order_by('-start_date')
    latest_assignment = Subquery(latest_assignment.values('id')[:1])

    # Update all positions
    Position.objects.update(current_assignment_id=latest_assignment)
