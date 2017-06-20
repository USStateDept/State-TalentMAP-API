from django.db import models


class Position(models.Model):
    '''
    The position model represents a job by combining different requirements, as
    well as geographic location
    '''

    # Positions can have any number of language requirements
    language_requirements = models.ManyToManyField('language.Qualification', related_name='positions')

    grade = models.ForeignKey('position.Grade', related_name='positions', null=True, help_text='The job grade for this position')


class Grade(models.Model):
    '''
    The grade model represents a job grade
    '''

    code = models.CharField(max_length=2, db_index=True, unique=True, null=False)
