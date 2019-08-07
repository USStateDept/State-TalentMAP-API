import logging

from django.utils import timezone
from django.db.models import Q, Value, Case, When, BooleanField
from django.db import models
from django.db.models.signals import pre_save, post_save, post_delete, m2m_changed
from django.dispatch import receiver
from django.contrib.postgres.fields import ArrayField

from simple_history.models import HistoricalRecords
from djchoices import DjangoChoices, ChoiceItem

import talentmap_api.position.models
from talentmap_api.common.models import StaticRepresentationModel
from talentmap_api.common.common_helpers import safe_navigation
from talentmap_api.messaging.models import Notification
from talentmap_api.user_profile.models import UserProfile

class CyclePosition(StaticRepresentationModel):
    '''
    Maps a position to a bid cycle with additional fields
    '''
    bidcycle = models.ForeignKey('bidding.BidCycle', on_delete=models.CASCADE, related_name="cycle_position_cycle")
    position = models.ForeignKey('position.Position', on_delete=models.CASCADE, related_name="cycle_position_position")

    ted = models.DateTimeField(null=True, help_text="The ted date for the cycle position")
    created = models.DateTimeField(null=True, help_text="The created date for the cycle positon")
    updated = models.DateTimeField(null=True, help_text="The updated date for the cycle positon")
    posted_date = models.DateTimeField(null=True, help_text="The posted date for the cycle positon")
    status_code = models.CharField(max_length=120, default="OP", null=True, help_text="Cycle status code")
    status = models.CharField(max_length=120, default="Open", null=True, help_text="Cycle status text")
    
    _cp_id = models.TextField(null=True)
    
    @property
    def similar_positions(self):
        '''
        Returns a query set of similar positions, using the base criteria.
        If there are not at least 3 results, the criteria is loosened.
        '''
        base_criteria = {
            "position__post__location__country__id": safe_navigation(self, "position.post.location.country.id"),
            "position__skill__code": safe_navigation(self, "position.skill.code"),
            "position__grade__code": safe_navigation(self, "position.grade.code"),
        }

        q_obj = models.Q(**base_criteria)
        position_ids = CyclePosition.objects.filter(status_code__in=["HS", "OP"]).values_list("position_id", flat=True)
        all_pos_queryset = CyclePosition.objects.filter(position_id__in=position_ids)
        queryset = all_pos_queryset.filter(q_obj).exclude(id=self.id)

        while queryset.count() < 3:
            del base_criteria[list(base_criteria.keys())[0]]
            q_obj = models.Q(**base_criteria)
            queryset = all_pos_queryset.filter(q_obj).exclude(id=self.id)
        return queryset
    
    @property
    def availability(self):
        '''
        Evaluates if this cycle position can accept new bids in it's latest bidcycle
        '''
        if self.bidcycle:
            available, reason = self.can_accept_new_bids(self.bidcycle)
            return {
                "availability": available,
                "reason": reason,
            }
        else:
            return {
                "availability": False,
                "reason": "This position is not in an available bid cycle",
            }
    
    def can_accept_new_bids(self, bidcycle):
        '''
        Evaluates if this position can accept new bids for the given bidcycle

        Args:
            - bidcycle (Object) - The Bidcycle object to evaluate if this position can accept a bid

        Returns:
            - Boolean - True if the position can accept new bids for the cycle, otherwise False
            - String - An explanation of why this position is not biddable
        '''
        # Filter this positions bid by bidcycle and our Q object
        q_obj = Bid.get_unavailable_status_filter()
        fulfilling_bids = Bid.objects.filter(position__id=self.id).filter(q_obj)
        if fulfilling_bids.exists():
            messages = {
                Bid.Status.handshake_offered: "This position has an outstanding handshake",
                Bid.Status.handshake_accepted: "This position has an accepted handshake",
                Bid.Status.in_panel: "This position is currently due for paneling",
                Bid.Status.approved: "This position has been filled",
            }
            return False, messages[fulfilling_bids.first().status]

        return True, ""

    def __str__(self):
        return f"[{self.position.position_number}] {self.position.title} ({self.position.post})"

    @property
    def availability(self):
        '''
        Evaluates if this cycle position can accept new bids in it's latest bidcycle
        '''
        if self.bidcycle:
            available, reason = self.can_accept_new_bids(self.bidcycle)
            return {
                "availability": available,
                "reason": reason,
            }
        else:
            return {
                "availability": False,
                "reason": "This position is not in an available bid cycle",
            }
    
    def can_accept_new_bids(self, bidcycle):
        '''
        Evaluates if this position can accept new bids for the given bidcycle

        Args:
            - bidcycle (Object) - The Bidcycle object to evaluate if this position can accept a bid

        Returns:
            - Boolean - True if the position can accept new bids for the cycle, otherwise False
            - String - An explanation of why this position is not biddable
        '''
        # Filter this positions bid by bidcycle and our Q object
        q_obj = Bid.get_unavailable_status_filter()
        fulfilling_bids = Bid.objects.filter(position__id=self.id).filter(q_obj)
        if fulfilling_bids.exists():
            messages = {
                Bid.Status.handshake_offered: "This position has an outstanding handshake",
                Bid.Status.handshake_accepted: "This position has an accepted handshake",
                Bid.Status.in_panel: "This position is currently due for paneling",
                Bid.Status.approved: "This position has been filled",
            }
            return False, messages[fulfilling_bids.first().status]

        return True, ""

    class Meta:
        managed = True
        ordering = ["bidcycle__cycle_start_date"]

class BidCycle(StaticRepresentationModel):
    '''
    The bid cycle model represents an individual bidding cycle
    '''

    name = models.TextField(null=False, help_text="The name of the bid cycle")
    cycle_start_date = models.DateTimeField(null=True, help_text="The start date for the bid cycle")
    cycle_deadline_date = models.DateTimeField(null=True, help_text="The deadline date for the bid cycle")
    cycle_end_date = models.DateTimeField(null=True, help_text="The end date for the bid cycle")
    active = models.BooleanField(default=False, help_text="Whether this bidcycle is active or not")

    positions = models.ManyToManyField('position.Position', related_name="bid_cycles")

    history = HistoricalRecords()

    _id = models.TextField(null=True)
    _positions_seq_nums = ArrayField(models.TextField(), default=list)
    _category_code = models.TextField(null=True)
    _cycle_status = models.TextField(null=True)

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
    bidcycle = models.ForeignKey(BidCycle, on_delete=models.DO_NOTHING, related_name="status_surveys")

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
    handshake_declined = models.IntegerField(default=0)
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
        handshake_declined = ChoiceItem("handshake_declined", "handshake_declined")
        in_panel = ChoiceItem("in_panel", "in_panel")
        approved = ChoiceItem("approved")
        declined = ChoiceItem("declined")
        closed = ChoiceItem("closed")

    status = models.TextField(default=Status.draft, choices=Status.choices)

    draft_date = models.DateTimeField(auto_now_add=True)
    submitted_date = models.DateTimeField(null=True, help_text="The date the bid was submitted")
    handshake_offered_date = models.DateTimeField(null=True, help_text="The date the handshake was offered")
    handshake_accepted_date = models.DateTimeField(null=True, help_text="The date the handshake was accepted")
    handshake_declined_date = models.DateTimeField(null=True, help_text="The date the handshake was declined")
    in_panel_date = models.DateTimeField(null=True, help_text="The date the bid was scheduled for panel")
    scheduled_panel_date = models.DateTimeField(null=True, help_text="The date of the paneling meeting")
    approved_date = models.DateTimeField(null=True, help_text="The date the bid was approved")
    declined_date = models.DateTimeField(null=True, help_text="The date the bid was declined")
    closed_date = models.DateTimeField(null=True, help_text="The date the bid was closed")

    bidcycle = models.ForeignKey('bidding.BidCycle', on_delete=models.CASCADE, related_name="bids", help_text="The bidcycle for this bid")
    user = models.ForeignKey('user_profile.UserProfile', on_delete=models.CASCADE, related_name="bidlist", help_text="The user owning this bid")
    position = models.ForeignKey('bidding.CyclePosition', on_delete=models.CASCADE, related_name="bids", help_text="The position this bid is for")
    is_priority = models.BooleanField(default=False, help_text="Flag indicating if this bid is the bidder's priority bid")
    panel_reschedule_count = models.IntegerField(default=0, help_text="The number of times this bid's panel date has been rescheduled")

    reviewer = models.ForeignKey('user_profile.UserProfile', on_delete=models.DO_NOTHING, null=True, related_name="reviewing_bids", help_text="The bureau reviewer for this bid")

    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id} {self.user}#{self.position.position.position_number} ({self.status})"

    @property
    def is_paneling_today(self):
        return timezone.now().date() == self.scheduled_panel_date.date()

    @property
    def can_delete(self):
        ''' Whether or not a bid can be deleted '''
        return self.status == Bid.Status.draft or (self.status == Bid.Status.submitted and self.bidcycle.active)

    @property
    def emp_id(self):
        return self.user.emp_id

    @staticmethod
    def get_approval_statuses():
        '''
        Returns an array of statuses that denote some approval of the bid (handshake->approved)
        '''
        return [Bid.Status.handshake_offered, Bid.Status.handshake_accepted, Bid.Status.in_panel, Bid.Status.approved]

    @staticmethod
    def get_priority_statuses():
        '''
        Returns an array of statuses that correspond to a priority bid (handshake_accepted->approved)
        '''
        return [Bid.Status.handshake_accepted, Bid.Status.in_panel, Bid.Status.approved]

    @staticmethod
    def get_unavailable_status_filter():
        '''
        Returns a Q object which will return bids which are unavailable for bids (i.e. at or further than handshake status)
        '''
        # We must not have a status of a handshake; or any status further in the process
        qualified_statuses = Bid.get_priority_statuses()

        q_obj = Q()
        # Here we construct a Q object looking for statuses matching any of the qualified statuses
        for status in qualified_statuses:
            q_obj = q_obj | Q(status=status)

        return q_obj

    def generate_status_messages(self):
        return {
            "handshake_offered_owner": f"Your bid for {self.position} has been offered a handshake.",
            "handshake_offered_other": f"A competing bid for {self.position} has been offered a handshake.",
            "in_panel_owner": f"Your bid for {self.position} has been scheduled for panel review.",
            "approved_owner": f"Your bid for {self.position} has been approved by panel.",
            "declined_owner": f"Your bid for {self.position} has been declined."
        }

    class Meta:
        managed = True
        ordering = ["bidcycle__cycle_start_date", "update_date"]


class Waiver(StaticRepresentationModel):
    '''
    The waiver model represents an individual waiver for a particular facet of a bid's requirements
    '''

    class Category(DjangoChoices):
        retirement = ChoiceItem('retirement')
        language = ChoiceItem('language')
        six_eight = ChoiceItem('six_eight', 'six_eight')
        fairshare = ChoiceItem('fairshare')
        skill = ChoiceItem('skill')

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

    bid = models.ForeignKey(Bid, on_delete=models.DO_NOTHING, related_name='waivers')
    position = models.ForeignKey('position.Position', on_delete=models.DO_NOTHING, related_name='waivers')
    user = models.ForeignKey('user_profile.UserProfile', on_delete=models.DO_NOTHING, related_name='waivers')

    reviewer = models.ForeignKey('user_profile.UserProfile', on_delete=models.DO_NOTHING, null=True, related_name='reviewed_waivers')

    description = models.TextField(null=True, help_text="Description of the waiver request")

    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    def generate_status_messages(self):
        return {
            "approved_owner": f"The requested waiver for {self.user} ({self.type} {self.category}) for position {self.position} has been approved.",
            "requested_cdo": f"{self.user} has requested a {self.type} {self.category} waiver for position {self.position}.",
            "denied_owner": f"The requested waiver for {self.user} ({self.type} {self.category}) for position {self.position} has been denied."
        }

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
            cp = CyclePosition.objects.create(bidcycle=instance, position_id=position_id)
            talentmap_api.position.models.PositionBidStatistics.objects.create(position=cp)
    elif action == "pre_remove":
        # Delete statistics items when removed from the bidcycle
        talentmap_api.position.models.PositionBidStatistics.objects.filter(position__bidcycle=instance, position_id__in=pk_set).delete()
        CyclePosition.objects.filter(bidcycle=instance, position_id__in=pk_set).delete()

    if action in ["post_add", "post_remove"]:
        for position_id in pk_set:
            pos = talentmap_api.position.models.Position.objects.get(pk=position_id)
            if pos.bid_cycles.filter(active=True).count() > 0:
                pos.latest_bidcycle = pos.bid_cycles.filter(active=True).latest('cycle_start_date')
            else:
                pos.latest_bidcycle = None
            pos.save()

@receiver(post_save, sender=BidCycle, dispatch_uid="bidcycle_active_changed")
def bidcycle_active_changed(sender, instance, **kwargs):
    '''
    Update positions latest_active_bidcycle field to latest acive bidcycle
    '''
    positions = talentmap_api.position.models.Position.objects.filter(id__in=instance.positions.values_list('id', flat=True))
    for pos in positions:
        if pos.bid_cycles.filter(active=True).count() > 0:
            pos.latest_bidcycle = pos.bid_cycles.filter(active=True).latest('cycle_start_date')
        else:
            pos.latest_bidcycle = None
        pos.save()

@receiver(pre_save, sender=Bid, dispatch_uid="bid_status_changed")
def bid_status_changed(sender, instance, **kwargs):
    notification_bodies = instance.generate_status_messages()

    # If our instance has an id, we're performing an update (and not a create)
    if instance.id:
        # Get our bid as it exists in the database
        old_bid = Bid.objects.get(id=instance.id)

        # Set the bid's priority flag
        instance.is_priority = instance.status in instance.get_priority_statuses()

        # Check if our old bid's status equals the new instance's status
        if old_bid.status != instance.status:
            # Create notifications for the owner of the bid, and other bidders on the same position
            owner = [instance.user]
            others = [x for x in instance.position.bids.values_list('user__id', flat=True) if x is not instance.user.id]
            others = list(UserProfile.objects.filter(id__in=others))
            for notification, users in [(f"{instance.status}_owner", owner), (f"{instance.status}_other", others)]:
                # If we have that notification status in the notification bodies, create the notification
                if notification in notification_bodies:
                    for user in users:
                        Notification.objects.create(owner=user,
                                                    tags=['bidding', f'{instance.status}'],
                                                    message=notification_bodies[notification])


@receiver(pre_save, sender=Bid, dispatch_uid="bid_panel_date_changed")
def bid_panel_date_changed(sender, instance, **kwargs):
    # If our instance has an id, we're performing an update (and not a create)
    if instance.id and instance.scheduled_panel_date and instance.status in [Bid.Status.handshake_accepted, Bid.Status.in_panel]:
        # Get our bid as it exists in the database
        old_bid = Bid.objects.get(id=instance.id)

        verb = 'scheduled'
        # If we have an old date, this a re-schedule
        if old_bid.scheduled_panel_date:
            verb = 'rescheduled'
            instance.panel_reschedule_count = old_bid.panel_reschedule_count + 1
        # Check if our old bid's paneling date is the same as the new one
        if old_bid.scheduled_panel_date != instance.scheduled_panel_date:
            Notification.objects.create(owner=instance.user,
                                        tags=['bidding', f'{instance.status}', f'{verb}'],
                                        message=f"Your bid for {instance.position} has been {verb} for paneling on {instance.scheduled_panel_date}.")


@receiver(post_save, sender=Bid, dispatch_uid="save_update_bid_statistics")
@receiver(post_delete, sender=Bid, dispatch_uid="delete_update_bid_statistics")
def delete_update_bid_statistics(sender, instance, **kwargs):
    # Get the position associated with this bid and update the statistics
    statistics, _ = talentmap_api.position.models.PositionBidStatistics.objects.get_or_create(position=instance.position)
    statistics.update_statistics()

    # Update the user's bid statistics
    statistics, _ = UserBidStatistics.objects.get_or_create(user=instance.user, bidcycle=instance.bidcycle)
    statistics.update_statistics()


@receiver(pre_save, sender=Waiver, dispatch_uid="waiver_status_changed")
def waiver_status_changed(sender, instance, **kwargs):
    notification_bodies = instance.generate_status_messages()

    # If our instance has an id, we're performing an update (and not a create)
    if instance.id:
        # Get our waiver as it exists in the database
        old_waiver = Waiver.objects.get(id=instance.id)
        # Check if our old waiver's status equals the new instance's status
        if old_waiver.status != instance.status:
            # Perform an action based upon the new status
            if instance.status is Waiver.Status.approved:
                Notification.objects.create(owner=instance.user,
                                            tags=['waiver', f'{instance.status}'],
                                            message=notification_bodies['approved_owner'])
            elif instance.status is Waiver.Status.denied:
                Notification.objects.create(owner=instance.user,
                                            tags=['waiver', f'{instance.status}'],
                                            message=notification_bodies['denied_owner'])

    else:
        # It's a new waiver request, notify the CDO
        if instance.user.cdo:
            Notification.objects.create(owner=instance.user.cdo,
                                        tags=['waiver', f'{instance.status}'],
                                        message=notification_bodies['requested_cdo'])
