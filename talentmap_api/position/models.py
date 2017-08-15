from django.db import models

from talentmap_api.organization.models import Organization, Post
from talentmap_api.language.models import Qualification


class Position(models.Model):
    '''
    The position model represents a job by combining different requirements, as
    well as geographic location
    '''

    position_number = models.TextField(null=True, help_text='The position number')
    title = models.TextField(null=True, help_text='The position title')

    # Positions can have any number of language requirements
    language_requirements = models.ManyToManyField('language.Qualification', related_name='positions')

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
    _language_1_written_proficiency_code = models.TextField(null=True)
    _language_2_spoken_proficiency_code = models.TextField(null=True)
    _language_2_written_proficiency_code = models.TextField(null=True)
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
                                                                 self._language_1_written_proficiency_code,
                                                                 self._language_1_spoken_proficiency_code)[0]
            if qualification:
                self.language_requirements.add(qualification)
        if self._language_2_code:
            qualification = Qualification.get_or_create_by_codes(self._language_2_code,
                                                                 self._language_2_written_proficiency_code,
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

        self.save()

    class Meta:
        managed = True
        ordering = ["position_number"]


class Grade(models.Model):
    '''
    The grade model represents an individual job grade
    '''

    code = models.TextField(db_index=True, unique=True, null=False)

    def __str__(self):
        return f"{self.code}"

    class Meta:
        managed = True
        ordering = ["code"]


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
