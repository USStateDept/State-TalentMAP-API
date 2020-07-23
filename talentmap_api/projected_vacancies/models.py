from django.db import models


class ProjectedVacancyFavorite(models.Model):

    fv_seq_num = models.TextField(null=False)
    user = models.ForeignKey('user_profile.UserProfile', null=False, on_delete=models.DO_NOTHING, help_text="The user to which this favorite belongs")
    archived = models.BooleanField(default=False)

    class Meta:
        managed = True
        ordering = ["fv_seq_num"]
        unique_together = ('fv_seq_num', 'user',)

