from django.db import models


class GlossaryEntry(models.Model):
    """
    Represents an individual entry in the glossary
    """

    title = models.TextField(null=False, unique=True)
    definition = models.TextField(null=False)
    link = models.TextField(blank=True, default='')

    last_editing_user = models.ForeignKey('user_profile.UserProfile', on_delete=models.DO_NOTHING, related_name='edited_glossary', null=True, help_text="The last user to edit this glossary entry")
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    is_archived = models.BooleanField(default=False, help_text="Denotes if this glossary item is archived")

    class Meta:
        managed = True
        ordering = ["title"]
