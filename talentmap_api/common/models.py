from django.db import models


class StaticRepresentationModel(models.Model):
    '''
    This model should be used as the base for any other object who uses a string representation during serialization
    this reduces the calculations and database calls required during serialization
    '''
    string_representation = models.TextField(null=True, blank=True, help_text="The string representation of this object")

    def save(self, *args, **kwargs):
        self.string_representation = str(self)
        super(StaticRepresentationModel, self).save(*args, **kwargs)

    class Meta:
        abstract = True
