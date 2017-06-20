from django.db import models


class Position(models.Model):
    '''
    The position model represents a job by combining different requirements, as
    well as geographic location
    '''

    # Positions can have any number of language requirements
    language_requirements = models.ManyToManyField('language.Qualification', related_name='positions')
