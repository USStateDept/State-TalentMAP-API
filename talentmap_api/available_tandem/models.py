from django.db import models

from talentmap_api.common.models import StaticRepresentationModel

class AvailableFavoriteTandem(StaticRepresentationModel):

    cp_id = models.TextField(null=False)
    user = models.ForeignKey('user_profile.UserProfile', null=False, on_delete=models.DO_NOTHING, help_text="The user to which this tandem favorite belongs")
    archived = models.BooleanField(default=False)

    class Meta:
        managed = True
        ordering = ["cp_id"]
        unique_together = ('cp_id', 'user',)
