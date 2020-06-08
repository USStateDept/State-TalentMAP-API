from django.db import models

class FeatureFlags(models.Model):
    '''
    Feature Flags content
    '''
    feature_flags = models.TextField(unique=True, null=True)
    date_updated = models.DateTimeField(auto_now_add=True, null=False)

    class Meta:
        managed = True
