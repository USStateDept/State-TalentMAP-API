from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

from djchoices import DjangoChoices, ChoiceItem

from talentmap_api.messaging.models import Notification
from talentmap_api.user_profile.models import UserProfile


class BidCycle(models.Model):
    '''
    The bid cycle model represents an individual bidding cycle
    '''

    name = models.TextField(null=False, help_text="The name of the bid cycle")
    cycle_start_date = models.DateField(null=False, help_text="The start date for the bid cycle")
    cycle_deadline_date = models.DateField(null=False, help_text="The deadline date for the bid cycle")
    cycle_end_date = models.DateField(null=False, help_text="The end date for the bid cycle")
    active = models.BooleanField(default=False, help_text="Whether this bidcycle is active or not")

    positions = models.ManyToManyField('position.Position', related_name="bid_cycles")

    def __str__(self):
        return f"{self.name}"

    class Meta:
        managed = True
        ordering = ["cycle_start_date"]


class Bid(models.Model):
    '''
    The bid object represents an individual bid, the position, user, and process status
    '''

    MAXIMUM_SUBMITTED_BIDS = 10

    class Status(DjangoChoices):
        draft = ChoiceItem("draft")
        submitted = ChoiceItem("submitted")
        handshake_offered = ChoiceItem("handshake offered")
        handshake_accepted = ChoiceItem("handshake accepted")
        declined = ChoiceItem("declined")
        closed = ChoiceItem("closed")

    status = models.TextField(default=Status.draft, choices=Status.choices)

    bidcycle = models.ForeignKey('bidding.BidCycle', on_delete=models.CASCADE, related_name="bids", help_text="The bidcycle for this bid")
    user = models.ForeignKey('user_profile.UserProfile', on_delete=models.CASCADE, related_name="bidlist", help_text="The user owning this bid")
    position = models.ForeignKey('position.Position', on_delete=models.CASCADE, related_name="bids", help_text="The position this bid is for")

    submission_date = models.DateField(null=True)

    def __str__(self):
        return f"{self.user}#{self.position.position_number}"

    class Meta:
        managed = True
        ordering = ["bidcycle__cycle_start_date", "submission_date"]


@receiver(pre_save, sender=Bid, dispatch_uid="notify_on_handshake")
def notify_on_handshake(sender, instance, **kwargs):
    # If our instance has an id, we're performing an update (and not a create)
    if instance.id:
        # Get our bid as it exists in the database
        old_bid = Bid.objects.get(id=instance.id)
        # Check if our old bid's status equals the new instance's status
        if old_bid.status is not instance.status:
            # Perform an action based upon the new status
            if instance.status is Bid.Status.handshake_offered:
                # Notify the owning user that their bid has been offered a handshake
                Notification.objects.create(owner=instance.user,
                                            message=f"Your bid for {instance.position} has been offered a handshake.")
                # Notify all other bidders that this position has a handshake offered
                # Get a list of all user profile ID's which aren't this user
                users = [x for x in instance.position.bids.values_list('user__id', flat=True) if x is not instance.user.id]
                for user in users:
                    Notification.objects.create(owner=UserProfile.objects.get(id=user),
                                                message=f"A competing bid for {instance.position} has been offered a handshake.")
            elif instance.status is Bid.Status.declined:
                # Notify the owning user that this bid has been declined
                Notification.objects.create(owner=instance.user,
                                            message=f"Your bid for {instance.position} has been declined.")
