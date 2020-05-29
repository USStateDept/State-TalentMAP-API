import logging

from django.utils import timezone
from django.db import models

from djchoices import DjangoChoices, ChoiceItem

from talentmap_api.common.common_helpers import safe_navigation


class Bid(models.Model):
    '''
    The bid object represents an individual bid, user, and process status
    '''

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

    class Meta:
        managed = False
