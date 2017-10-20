from django.db import models
from djchoices import DjangoChoices, ChoiceItem
from django.db.models.signals import post_save
from django.dispatch import receiver

import datetime
from dateutil.relativedelta import relativedelta

from talentmap_api.organization.models import Organization, Post
from talentmap_api.language.models import Qualification


class Position(models.Model):
    '''
    The position model represents a job by combining different requirements, as
    well as geographic location
    '''

    position_number = models.TextField(null=True, help_text='The position number')
    description = models.OneToOneField('position.CapsuleDescription', related_name='position', null=True, help_text="A plain text description of the position")
    title = models.TextField(null=True, help_text='The position title')

    # Positions can have any number of language requirements
    language_requirements = models.ManyToManyField('language.Qualification', related_name='positions')

    # Positions can have any number of classifications
    classifications = models.ManyToManyField('position.Classification', related_name='positions')
    current_assignment = models.ForeignKey('position.Assignment', null=True, related_name='current_for_position')

    grade = models.ForeignKey('position.Grade', related_name='positions', null=True, help_text='The job grade for this position')
    skill = models.ForeignKey('position.Skill', related_name='positions', null=True, help_text='The job skill for this position')

    organization = models.ForeignKey('organization.Organization', related_name='organization_positions', null=True, help_text='The organization for this position')
    bureau = models.ForeignKey('organization.Organization', related_name='bureau_positions', null=True, help_text='The bureau for this position')
    post = models.ForeignKey('organization.post', related_name='positions', null=True, help_text='The position post')

    is_overseas = models.BooleanField(default=False, help_text="Flag designating whether the position is overseas")

    create_date = models.DateField(null=True, help_text="The creation date of the position")
    update_date = models.DateField(null=True, help_text="The update date of this position")
    effective_date = models.DateField(null=True, help_text="The effective date of this position")

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

    def __str__(self):
        return f"[{self.position_number}] {self.title} ({self.post})"

    def update_relationships(self):
        '''
        Update the position relationships
        '''
        # Update language requirements
        self.language_requirements.clear()
        if self._language_1_code:
            qualification = Qualification.get_or_create_by_codes(self._language_1_code,
                                                                 self._language_1_reading_proficiency_code,
                                                                 self._language_1_spoken_proficiency_code)[0]
            if qualification:
                self.language_requirements.add(qualification)
        if self._language_2_code:
            qualification = Qualification.get_or_create_by_codes(self._language_2_code,
                                                                 self._language_2_reading_proficiency_code,
                                                                 self._language_2_spoken_proficiency_code)[0]
            if qualification:
                self.language_requirements.add(qualification)

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


class CapsuleDescription(models.Model):
    '''
    Represents a capsule description, describing the associated object in plain English
    '''

    content = models.TextField(null=True)
    point_of_contact = models.TextField(null=True)
    website = models.TextField(null=True)

    last_editing_user = models.ForeignKey('user_profile.UserProfile', related_name='edited_capsule_descriptions', null=True, help_text="The last user to edit this description")
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    _pos_seq_num = models.TextField(null=True)

    class Meta:
        managed = True
        ordering = ["date_updated"]


class Grade(models.Model):
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


class Skill(models.Model):
    '''
    The skill model represents an individual job skill
    '''

    code = models.TextField(db_index=True, unique=True, null=False, help_text="4 character string code representation of the job skill")
    description = models.TextField(null=False, help_text="Text description of the job skill")

    def __str__(self):
        return f"{self.description} ({self.code})"

    class Meta:
        managed = True
        ordering = ["code"]


class Classification(models.Model):
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


class Assignment(models.Model):
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
        service_need = ChoiceItem("service_need")
        compassionate = ChoiceItem("compassionate")
        other = ChoiceItem("other")

    status = models.TextField(default=Status.pending, choices=Status.choices)
    curtailment_reason = models.TextField(null=True, choices=CurtailmentReason.choices)

    user = models.ForeignKey('user_profile.UserProfile', related_name='assignments')
    position = models.ForeignKey('position.Position', related_name='assignments')
    tour_of_duty = models.ForeignKey('organization.TourOfDuty', related_name='assignments')

    create_date = models.DateField(auto_now_add=True, help_text='The date the assignment was created')
    start_date = models.DateField(null=True, help_text='The date the assignment started')
    estimated_end_date = models.DateField(null=True, help_text='The estimated end date based upon tour of duty')
    end_date = models.DateField(null=True, help_text='The date this position was completed or curtailed')
    update_date = models.DateField(auto_now=True)

    def save(self, *args, **kwargs):
        # Set the estimate end date to the date in the future based on tour of duty months
        if self.start_date and self.tour_of_duty:
            self.estimated_end_date = datetime.datetime.strptime(self.start_date, '%Y-%m-%d').date() + relativedelta(months=self.tour_of_duty.months)
        super(Assignment, self).save(*args, **kwargs)

    def __str__(self):
        return f"({self.status}) {self.user} at {self.position}"

    class Meta:
        managed = True
        ordering = ["update_date"]


# Signal listeners
@receiver(post_save, sender=Assignment, dispatch_uid="assignment_post_save")
def assignment_post_save(sender, instance, created, **kwargs):
    '''
    This listener updates an assignment's position with its new current assignment
    '''
    position = instance.position
    if position.assignments.count() > 0:
        position.current_assignment = position.assignments.latest("start_date")
    else:
        position.current_assignment = None
    position.save()
