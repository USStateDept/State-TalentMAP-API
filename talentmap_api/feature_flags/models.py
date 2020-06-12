from django.db import models
from django.contrib.postgres.fields import JSONField

class FeatureFlags(models.Model):
    '''
    Feature Flags content
    '''
    feature_flags = JSONField(default=dict, unique=False)
    date_updated = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        ordering = ["date_updated"]
