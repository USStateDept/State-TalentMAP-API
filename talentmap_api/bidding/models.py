from django.db import models


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
