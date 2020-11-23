from django.db import models

class AvailableBidders(models.Model):
    STATUS_CHOICES = [
        ('UA', 'Unassigned'),
        ('IT', 'In-Transit'),
        ('OC', 'Over-Complement'),
        ('LWOP', 'Leave Without Pay'),
    ]
    bidder_perdet = models.ForeignKey('user_profile.UserProfile', related_name='client', null=False, on_delete=models.DO_NOTHING, help_text="The user in availableBidders list")
    status = models.CharField(
        max_length=2,
        choices=STATUS_CHOICES,
        default='UA',
    )
    oc_reason = models.CharField(max_length=255, null=False, blank=True)
    comments = models.CharField(max_length=255, null=False, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    is_shared = models.BooleanField(default=False, help_text="Shared with Bureau")
    last_editing_user_id = models.ForeignKey('user_profile.UserProfile', related_name='agent', null=False, on_delete=models.DO_NOTHING, help_text="The last user to edit")

    class Meta:
        managed = True
        ordering = ["date_created"]
        unique_together = ('bidder_perdet',)
