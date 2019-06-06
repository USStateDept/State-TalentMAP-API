from django.db import models

from talentmap_api.common.models import StaticRepresentationModel

class HomepageBanner(StaticRepresentationModel):
    '''
    The banner for the homepage
    '''
    text = models.TextField(null=False, help_text="The text for the banner")
    is_visible = models.BooleanField(default=False)

    class Meta:
        managed = True

