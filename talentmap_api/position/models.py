import itertools

from django.db.models import OuterRef, Subquery
from django.db import models
from djchoices import DjangoChoices, ChoiceItem
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

from dateutil.relativedelta import relativedelta

import talentmap_api.bidding.models
from talentmap_api.common.common_helpers import ensure_date, month_diff, safe_navigation
from talentmap_api.common.models import StaticRepresentationModel


class Grade(StaticRepresentationModel):
    '''
    The grade model represents an individual job grade
    '''
    # All valid grade codes, and their ranked order. Using a dict instead of a list
    # to avoid try/catch in the save override when getting ranks
    RANK_ORDERING = {
        "CA": 1,
        "CM": 2,
        "MC": 3,
        "OC": 4,
        "OM": 5,
        "00": 6,
        "01": 7,
        "02": 8,
        "03": 9,
        "04": 10,
        "05": 11,
        "06": 12,
        "07": 13,
        "08": 14,
    }

    code = models.CharField(max_length=50, db_index=True, unique=True, null=False)
    rank = models.IntegerField(null=False, default=0)

    def __str__(self):
        return f"{self.code}"

    def update_relationships(self):
        self.rank = Grade.RANK_ORDERING.get(self.code, 0)
        self.save()

    class Meta:
        managed = True
        ordering = ["rank"]


class Skill(StaticRepresentationModel):
    '''
    The skill model represents an individual job skill
    '''

    code = models.CharField(max_length=50, db_index=True, unique=True, null=False, help_text="4 character string code representation of the job skill")
    description = models.CharField(max_length=50, null=False, help_text="Text description of the job skill")

    def __str__(self):
        return f"{self.description} ({self.code})"

    class Meta:
        managed = True
        ordering = ["code"]


class SkillCone(StaticRepresentationModel):
    '''
    The skill cone represents a grouping of skills
    '''

    name = models.CharField(max_length=50, db_index=True, null=False, help_text="The name of the skill cone")

    # Data as loaded from XML
    _id = models.TextField(null=True)
    _skill_codes = models.TextField(null=True, blank=True, default="")

    @property
    def skill_codes(self):
        '''
        Returns the string list of skill codes as an array
        '''
        return self._skill_codes.split(',')

    @skill_codes.setter
    def skill_codes(self, value):
        '''
        Sets the skill code string to the joined array value
        '''
        if not value:
            value = [""]
        self._skill_codes = ','.join(value)

    def update_relationships(self):
        # Get all other skill cones with the same _id
        same_cone = SkillCone.objects.filter(_id=self._id).exclude(id=self.id)
        skill_codes = self.skill_codes

        if same_cone.count() > 0:
            # Add their skill codes to our skill code list
            new_codes = [x.skill_codes for x in list(same_cone)]
            if len(new_codes) > 0:
                # Use chain to flatten the list of lists
                skill_codes += list(itertools.chain.from_iterable(new_codes))
                # Eliminate duplicates
                skill_codes = list(set(skill_codes))
                # Set the data
                self.skill_codes = skill_codes
                # Save this cone
                self.save()

        # Update all skills to point to this cone
        Skill.objects.filter(code__in=skill_codes).update(cone=self)

        # Delete the duplicate cones
        same_cone.delete()

    def __str__(self):
        return f"{self.name}"

    class Meta:
        managed = True
        ordering = ["name"]


class Classification(StaticRepresentationModel):
    '''
    The position classification model represents a position's classification.
    Maintained as a separate model to support limiting visibility.
    '''

    code = models.CharField(max_length=50, db_index=True, unique=True, null=False, help_text="The classification code")
    description = models.CharField(max_length=50, null=False, help_text="Text description of the classification")

    def __str__(self):
        return f"{self.description} ({self.code})"

    class Meta:
        managed = True
        ordering = ["code"]
