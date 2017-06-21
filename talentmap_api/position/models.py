from django.db import models


class Position(models.Model):
    '''
    The position model represents a job by combining different requirements, as
    well as geographic location
    '''

    # Positions can have any number of language requirements
    language_requirements = models.ManyToManyField('language.Qualification', related_name='positions')

    grade = models.ForeignKey('position.Grade', related_name='positions', null=True, help_text='The job grade for this position')
    skill = models.ForeignKey('position.Skill', related_name='positions', null=True, help_text='The job skill for this position')

    organization = models.ForeignKey('organization.Organization', related_name='organization_positions', null=True, help_text='The organization for this position')
    bureau = models.ForeignKey('organization.Organization', related_name='bureau_positions', null=True, help_text='The bureau for this position')


class Grade(models.Model):
    '''
    The grade model represents an individual job grade
    '''

    code = models.CharField(max_length=2, db_index=True, unique=True, null=False)

    def __str__(self):
        return "{}".format(self.code)


class Skill(models.Model):
    '''
    The skill model represents an individual job skill
    '''

    code = models.CharField(max_length=4, db_index=True, unique=True, null=False, help_text="4 character string code representation of the job skill")
    description = models.TextField(null=False, help_text="Text description of the job skill")

    def __str__(self):
        return "{} ({})".format(self.description, self.code)
