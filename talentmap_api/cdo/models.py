from django.db import models

class AvailableBidders(models.Model):
    STATUS_CHOICES = [
        ('UA', 'Unassigned'),
        ('IT', 'In-Transit'),
        ('OC', 'Over-Complement'),
        ('AWOL', 'AWOL'),
        ('', ''),
    ]
    bidder_perdet = models.CharField(max_length=255, null=False, help_text="The user in availableBidders list")
    status = models.CharField(
        max_length=4,
        choices=STATUS_CHOICES,
        default='',
    )
    oc_reason = models.CharField(max_length=255, null=False, blank=True)
    oc_bureau = models.CharField(max_length=255, null=False, blank=True)
    comments = models.CharField(max_length=255, null=False, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now_add=True)
    archived = models.BooleanField(default=False)
    is_shared = models.BooleanField(default=False, help_text="Shared with Bureau")
    last_editing_user = models.ForeignKey('user_profile.UserProfile', related_name='agent', null=False, on_delete=models.DO_NOTHING, help_text="The last user to edit")
    step_letter_one = models.DateTimeField(null=True)
    step_letter_two = models.DateTimeField(null=True)

    class Meta:
        managed = True
        ordering = ["date_created"]
        unique_together = ('bidder_perdet',)
