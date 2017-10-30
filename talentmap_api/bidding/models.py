from django.db import models
from django.db.models.signals import pre_save, post_save, post_delete, m2m_changed
from django.dispatch import receiver

from djchoices import DjangoChoices, ChoiceItem

from talentmap_api.position.models import PositionBidStatistics
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


class StatusSurvey(models.Model):
    '''
    The status survey model represents eligiblity status self-identification information
    on a per-bidcycle basis
    '''

    user = models.ForeignKey("user_profile.UserProfile", on_delete=models.CASCADE, related_name="status_surveys")
    bidcycle = models.ForeignKey(BidCycle, related_name="status_surveys")

    is_differential_bidder = models.BooleanField(default=False)
    is_fairshare = models.BooleanField(default=False)
    is_six_eight = models.BooleanField(default=False)

    class Meta:
        managed = True
        ordering = ["bidcycle"]
        unique_together = (("user", "bidcycle"),)


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
        in_panel = ChoiceItem("in panel")
        approved = ChoiceItem("approved")
        declined = ChoiceItem("declined")
        closed = ChoiceItem("closed")

    status = models.TextField(default=Status.draft, choices=Status.choices)

    bidcycle = models.ForeignKey('bidding.BidCycle', on_delete=models.CASCADE, related_name="bids", help_text="The bidcycle for this bid")
    user = models.ForeignKey('user_profile.UserProfile', on_delete=models.CASCADE, related_name="bidlist", help_text="The user owning this bid")
    position = models.ForeignKey('position.Position', on_delete=models.CASCADE, related_name="bids", help_text="The position this bid is for")

    submission_date = models.DateField(null=True)
    update_date = models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.user}#{self.position.position_number}"

    def generate_status_messages(self):
        return {
            "handshake_offered_owner": f"Your bid for {self.position} has been offered a handshake.",
            "handshake_offered_other": f"A competing bid for {self.position} has been offered a handshake.",
            "in_panel_owner": f"Your bid for {self.position} is under panel review.",
            "approved_owner": f"Your bid for {self.position} has been approved by panel.",
            "declined_owner": f"Your bid for {self.position} has been declined."
        }

    class Meta:
        managed = True
        ordering = ["bidcycle__cycle_start_date", "submission_date"]


@receiver(m2m_changed, sender=BidCycle.positions.through, dispatch_uid="bidcycle_m2m_changed")
def bidcycle_positions_update(sender, instance, action, reverse, model, pk_set, **kwargs):
    if action == "pre_add":
        # Create a new statistics item when a position is placed in the bid cycle
        for position_id in pk_set:
            PositionBidStatistics.objects.create(bidcycle=instance, position_id=position_id)
    elif action == "pre_remove":
        # Delete statistics items when removed from the bidcycle
        PositionBidStatistics.objects.filter(bidcycle=instance, position_id__in=pk_set).delete()


@receiver(pre_save, sender=Bid, dispatch_uid="bid_status_changed")
def bid_status_changed(sender, instance, **kwargs):
    notification_bodies = instance.generate_status_messages()

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
                                            message=notification_bodies["handshake_offered_owner"])
                # Notify all other bidders that this position has a handshake offered
                # Get a list of all user profile ID's which aren't this user
                users = [x for x in instance.position.bids.values_list('user__id', flat=True) if x is not instance.user.id]
                for user in users:
                    Notification.objects.create(owner=UserProfile.objects.get(id=user),
                                                message=notification_bodies["handshake_offered_other"])
            elif instance.status is Bid.Status.declined:
                # Notify the owning user that this bid has been declined
                Notification.objects.create(owner=instance.user,
                                            message=notification_bodies["declined_owner"])

            elif instance.status is Bid.Status.in_panel:
                # Notify the owning user that this bid is now under panel review
                Notification.objects.create(owner=instance.user,
                                            message=notification_bodies["in_panel_owner"])

            elif instance.status is Bid.Status.approved:
                # Notify the owning user that this bid has been accepted
                Notification.objects.create(owner=instance.user,
                                            message=notification_bodies["approved_owner"])


@receiver(post_save, sender=Bid, dispatch_uid="save_update_bid_statistics")
def save_update_bid_statistics(sender, instance, **kwargs):
    # Get the position associated with this bid and update the statistics
    instance.position.bid_statistics.get(bidcycle=instance.bidcycle).update_statistics()


@receiver(post_delete, sender=Bid, dispatch_uid="delete_update_bid_statistics")
def delete_update_bid_statistics(sender, instance, **kwargs):
    # Get the position associated with this bid and update the statistics
    instance.position.bid_statistics.get(bidcycle=instance.bidcycle).update_statistics()
