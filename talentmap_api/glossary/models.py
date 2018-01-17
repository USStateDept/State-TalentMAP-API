from django.db import models


class GlossaryEntry(models.Model):
    """
    Represents an individual entry in the glossary
    """

    title = models.TextField(null=False, unique=True)
    definition = models.TextField(null=False)
    link = models.TextField(blank=True, default='')

    class Meta:
        managed = True
        ordering = ["title"]
