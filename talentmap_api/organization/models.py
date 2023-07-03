from django.db import models

from talentmap_api.common.models import StaticRepresentationModel


class Obc(StaticRepresentationModel):
    '''
    Represents a country
    '''

    code = models.CharField(max_length=255, db_index=True, unique=True, null=False, help_text="The unique location code")
    short_name = models.TextField(null=True, help_text="The short name of the location")
    obc_id = models.TextField(null=True, help_text="The OBC ID for this location")

    class Meta:
        managed = True
        ordering = ["code"]
