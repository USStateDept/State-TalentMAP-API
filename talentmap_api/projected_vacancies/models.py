from django.db import models

from talentmap_api.common.models import StaticRepresentationModel

class ProjectedVacancyFavorite(StaticRepresentationModel):
  
  fv_seq_number = models.TextField(null=False)
  user = models.ForeignKey('user_profile.UserProfile', null=False, on_delete=models.DO_NOTHING, help_text="The user to which this favorite belongs")

  class Meta:
    managed = True
    ordering = ["fv_seq_number"]
    unique_together = ('fv_seq_number', 'user',)



