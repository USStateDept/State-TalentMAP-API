from django.db.models import Q, Value, Case, When, BooleanField
from django.db import models
from django.db.models.signals import pre_save, post_save, post_delete, m2m_changed
from django.dispatch import receiver

from djchoices import DjangoChoices, ChoiceItem

import talentmap_api.position.models
from talentmap_api.common.models import StaticRepresentationModel
from talentmap_api.messaging.models import Notification
from talentmap_api.user_profile.models import UserProfile


class BidCycle(StaticRepresentationModel):
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

    @property
    def annotated_positions(self):
        '''
        Returns a queryset of all positions, annotated with whether it is accepting bids or not
        '''
        bids = self.bids.filter(Bid.get_unavailable_status_filter()).values_list('position_id', flat=True)
        case = Case(When(id__in=bids,
                         then=Value(False)),
                    default=Value(True),
                    output_field=BooleanField())

        positions = self.positions.annotate(accepting_bids=case)

        return positions

    class Meta:
        managed = True
        ordering = ["cycle_start_date"]


class StatusSurvey(StaticRepresentationModel):
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


class UserBidStatistics(StaticRepresentationModel):
    '''
    Stores bid statistics for any particular bidcycle for each user
    '''
    bidcycle = models.ForeignKey('bidding.BidCycle', on_delete=models.CASCADE, related_name='user_bid_statistics')
    user = models.ForeignKey('user_profile.UserProfile', on_delete=models.CASCADE, related_name='bid_statistics')

    draft = models.IntegerField(default=0)
    submitted = models.IntegerField(default=0)
    handshake_offered = models.IntegerField(default=0)
    handshake_accepted = models.IntegerField(default=0)
    in_panel = models.IntegerField(default=0)
    approved = models.IntegerField(default=0)
    declined = models.IntegerField(default=0)
    closed = models.IntegerField(default=0)

    def update_statistics(self):
        for status_code, _ in Bid.Status.choices:
            setattr(self, status_code, Bid.objects.filter(user=self.user, bidcycle=self.bidcycle, status=status_code).count())

        self.save()

    class Meta:
        managed = True
        ordering = ["bidcycle__cycle_start_date"]
        unique_together = (("bidcycle", "user",),)


class Bid(StaticRepresentationModel):
    '''
    The bid object represents an individual bid, the position, user, and process status
    '''

    MAXIMUM_SUBMITTED_BIDS = 10

    class Status(DjangoChoices):
        draft = ChoiceItem("draft")
        submitted = ChoiceItem("submitted")
        handshake_offered = ChoiceItem("handshake_offered", "handshake_offered")
        handshake_accepted = ChoiceItem("handshake_accepted", "handshake_accepted")
        in_panel = ChoiceItem("in_panel", "in_panel")
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
        return f"{self.user}#{self.position.position_number} ({self.status})"

    @staticmethod
    def get_approval_statuses():
        '''
        Returns an array of statuses that denote some approval of the bid (handshake->approved)
        '''
        return [Bid.Status.handshake_offered, Bid.Status.handshake_accepted, Bid.Status.in_panel, Bid.Status.approved]

    @staticmethod
    def get_unavailable_status_filter():
        '''
        Returns a Q object which will return bids which are unavailable for bids (i.e. at or further than handshake status)
        '''
        # We must not have a status of a handshake; or any status further in the process
        qualified_statuses = Bid.get_approval_statuses()

        q_obj = Q()
        # Here we construct a Q object looking for statuses matching any of the qualified statuses
        for status in qualified_statuses:
            q_obj = q_obj | Q(status=status)

        return q_obj

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


class Waiver(StaticRepresentationModel):
    '''
    The waiver model represents an individual waiver for a particular facet of a bid's requirements
    '''

    class Category(DjangoChoices):
        retirement = ChoiceItem('retirement')
        language = ChoiceItem('language')
        six_eight = ChoiceItem('six_eight', 'six_eight')
        fairshare = ChoiceItem('fairshare')

    class Type(DjangoChoices):
        partial = ChoiceItem("partial")
        full = ChoiceItem("full")

    class Status(DjangoChoices):
        approved = ChoiceItem("approved")
        requested = ChoiceItem("requested")
        denied = ChoiceItem("denied")

    category = models.TextField(choices=Category.choices)
    type = models.TextField(default=Type.full, choices=Type.choices)
    status = models.TextField(default=Status.requested, choices=Status.choices)

    bid = models.ForeignKey(Bid, related_name='waivers')
    position = models.ForeignKey('position.Position', related_name='waivers')
    user = models.ForeignKey('user_profile.UserProfile', related_name='waivers')

    description = models.TextField(null=True, help_text="Description of the waiver request")

    create_date = models.DateField(auto_now_add=True)
    update_date = models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.type} {self.category} for {self.user} at {self.position}, {self.status}"

    class Meta:
        managed = True
        ordering = ["update_date"]


@receiver(m2m_changed, sender=BidCycle.positions.through, dispatch_uid="bidcycle_m2m_changed")
def bidcycle_positions_update(sender, instance, action, reverse, model, pk_set, **kwargs):
    if action == "pre_add":
        # Create a new statistics item when a position is placed in the bid cycle
        for position_id in pk_set:
            talentmap_api.position.models.PositionBidStatistics.objects.create(bidcycle=instance, position_id=position_id)
    elif action == "pre_remove":
        # Delete statistics items when removed from the bidcycle
        talentmap_api.position.models.PositionBidStatistics.objects.filter(bidcycle=instance, position_id__in=pk_set).delete()


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
                                            tags=['bidding'],
                                            message=notification_bodies["handshake_offered_owner"])
                # Notify all other bidders that this position has a handshake offered
                # Get a list of all user profile ID's which aren't this user
                users = [x for x in instance.position.bids.values_list('user__id', flat=True) if x is not instance.user.id]
                for user in users:
                    Notification.objects.create(owner=UserProfile.objects.get(id=user),
                                                tags=['bidding'],
                                                message=notification_bodies["handshake_offered_other"])
            elif instance.status is Bid.Status.declined:
                # Notify the owning user that this bid has been declined
                Notification.objects.create(owner=instance.user,
                                            tags=['bidding'],
                                            message=notification_bodies["declined_owner"])

            elif instance.status is Bid.Status.in_panel:
                # Notify the owning user that this bid is now under panel review
                Notification.objects.create(owner=instance.user,
                                            tags=['bidding'],
                                            message=notification_bodies["in_panel_owner"])

            elif instance.status is Bid.Status.approved:
                # Notify the owning user that this bid has been accepted
                Notification.objects.create(owner=instance.user,
                                            tags=['bidding'],
                                            message=notification_bodies["approved_owner"])


@receiver(post_save, sender=Bid, dispatch_uid="save_update_bid_statistics")
@receiver(post_delete, sender=Bid, dispatch_uid="delete_update_bid_statistics")
def delete_update_bid_statistics(sender, instance, **kwargs):
    # Get the position associated with this bid and update the statistics
    statistics, _ = talentmap_api.position.models.PositionBidStatistics.objects.get_or_create(bidcycle=instance.bidcycle, position=instance.position)
    statistics.update_statistics()

    # Update the user's bid statistics
    statistics, _ = UserBidStatistics.objects.get_or_create(user=instance.user, bidcycle=instance.bidcycle)
    statistics.update_statistics()
