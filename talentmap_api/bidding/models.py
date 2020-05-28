import logging

from django.utils import timezone
from django.db.models import Q, Value, Case, When, BooleanField
from django.db import models
from django.db.models.signals import pre_save, post_save, post_delete, m2m_changed
from django.dispatch import receiver

from djchoices import DjangoChoices, ChoiceItem

from talentmap_api.common.models import StaticRepresentationModel
from talentmap_api.common.common_helpers import safe_navigation
from talentmap_api.messaging.models import Notification
from talentmap_api.user_profile.models import UserProfile


class Bid(StaticRepresentationModel):
    '''
    The bid object represents an individual bid, user, and process status
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
        handshake_needs_registered = ChoiceItem("handshake_needs_registered", "handshake_needs_registered")

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

    user = models.ForeignKey('user_profile.UserProfile', on_delete=models.CASCADE, related_name="bidlist", help_text="The user owning this bid")
    is_priority = models.BooleanField(default=False, help_text="Flag indicating if this bid is the bidder's priority bid")

    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

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

    class Meta:
        managed = True
        ordering = ["bidcycle__cycle_start_date", "update_date"]
