from django.db import models

from djchoices import DjangoChoices, ChoiceItem


class BidCycle(models.Model):
    '''
    The bid cycle model represents an individual bidding cycle
    '''

    name = models.TextField(null=False, help_text="The name of the bid cycle")
    cycle_start_date = models.DateField(null=False, help_text="The start date for the bid cycle")
    cycle_end_date = models.DateField(null=False, help_text="The end date for the bid cycle")

    positions = models.ManyToManyField('position.Position', related_name="bid_cycles")

    class Meta:
        managed = True
        ordering = ["cycle_start_date"]


class Bid(models.Model):
    '''
    The bid object represents an individual bid, the position, user, and process status
    '''

    class Status(DjangoChoices):
        draft = ChoiceItem("draft")
        submitted = ChoiceItem("submitted")
        handshake_offered = ChoiceItem("handshake offered")
        handshake_accepted = ChoiceItem("handshake accepted")

    status = models.TextField(default=Status.draft, choices=Status.choices)

    bidcycle = models.ForeignKey('bidding.BidCycle', on_delete=models.CASCADE, help_text="The bidcycle for this bid")
    user = models.ForeignKey('user_profile.UserProfile', on_delete=models.CASCADE, help_text="The user owning this bid")
    position = models.ForeignKey('position.Position', on_delete=models.CASCADE, help_text="The position this bid is for")
