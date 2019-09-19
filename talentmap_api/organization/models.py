from django.db import models
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import ArrayField
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

import logging

import talentmap_api.position.models
from talentmap_api.common.models import StaticRepresentationModel


class Organization(StaticRepresentationModel):
    '''
    The organization model represents a DoS organization, such as bureaus
    '''

    code = models.TextField(db_index=True, unique=True, null=False, help_text="The organization code")
    long_description = models.TextField(null=False, help_text="Long-format description of the organization")
    short_description = models.TextField(null=False, help_text="Short-format description of the organization")

    location = models.ForeignKey('organization.Location', on_delete=models.SET_NULL, null=True, related_name="organizations", help_text="The location of this organization")

    # An organization is a Bureau if its bureau code is the same as its code
    is_bureau = models.BooleanField(default=False, help_text="Boolean indicator if this organization is a bureau")
    # An organization is a regional organization if it's parent organization code is 000000
    is_regional = models.BooleanField(default=False, help_text="Boolean indicator if this organization is regional")

    parent_organization = models.ForeignKey('organization.Organization', on_delete=models.SET_NULL, null=True, related_name="organizion_children", help_text="The parent organization of this organization")
    bureau_organization = models.ForeignKey('organization.Organization', on_delete=models.SET_NULL, null=True, related_name="bureau_children", help_text="The parent Bureau for this organization")

    # List of highlighted positions
    highlighted_positions = models.ManyToManyField('position.Position', related_name='highlighted_by_org', help_text="Positions which have been designated as highlighted by this organization")

    # These fields are used during loading to preserve source coded data, before the FK relationships are set
    # These also preserve the data should the FK items be deleted
    _parent_organization_code = models.TextField(null=True, help_text="Organization Code of the parent Organization")
    _parent_bureau_code = models.TextField(null=True, help_text="Bureau Code of the parent parent Bureau")
    _location_code = models.TextField(null=True, help_text="The location code for this organization")

    def update_relationships(self):
        '''
        Update the organization relationships, using the codes stored in the _parent fields.
        '''
        if self._parent_bureau_code:
            if self._parent_bureau_code == self.code:
                self.is_bureau = True
            if not self.is_bureau:
                bureau = Organization.objects.filter(code=self._parent_bureau_code)
                if bureau.count() != 1:
                    logging.getLogger(__name__).warn(f"While setting organization relationships, got {bureau.count()} values for bureau code {self._parent_bureau_code}")
                else:
                    self.bureau_organization = bureau.first()
        if self._parent_organization_code:
            org = Organization.objects.filter(code=self._parent_organization_code)
            if org.count() != 1:
                logging.getLogger(__name__).warn(f"While setting organization relationships, got {org.count()} values for org code {self._parent_organization_code}")
            else:
                self.parent_organization = org.first()

        if self._location_code:
            loc = Location.objects.filter(code=self._location_code)
            if loc.count() != 1:
                logging.getLogger(__name__).warn(f"While setting organization location, got {loc.count()} values for location code {self._location_code}")
            else:
                self.location = loc.first()

        regional_codes = [
            "110000",
            "120000",
            "130000",
            "140000",
            "146000",
            "150000",
            "160000"
        ]
        if self.code in regional_codes:
            self.is_regional = True

        self.save()

        if self.is_bureau:
            self.create_permissions()

        # Create our organization groups if they don't exist
        OrganizationGroup.create_groups()

    def create_permissions(self):
        '''
        Creates this organization's permission set
        '''
        # Create a group for AOs for this bureau
        group_name = f"bureau_ao:{self.code}"
        group, created = Group.objects.get_or_create(name=group_name)

        if created:
            logging.getLogger(__name__).info(f"Created permission group {group_name}")

        # Highlight action
        permission_codename = f"can_highlight_positions:{self.code}"
        permission_name = f"Can highlight positions for {self.short_description} ({self.code})"
        content_type = ContentType.objects.get_for_model(type(self))

        permission, created = Permission.objects.get_or_create(codename=permission_codename,
                                                               name=permission_name,
                                                               content_type=content_type)

        if created:
            logging.getLogger(__name__).info(f"Created permission {permission}")

        # Add the highlight permission to the AO group
        group.permissions.add(permission)

    def __str__(self):
        return f"({self.short_description}) {self.long_description}"

    class Meta:
        managed = True
        ordering = ["code"]


class OrganizationGroup(StaticRepresentationModel):
    '''
    Represents a logical grouping of organizations
    '''

    name = models.TextField(null=False, help_text="The description of the organization grouping")
    organizations = models.ManyToManyField('organization.Organization', related_name="groups")
    _org_codes = ArrayField(models.TextField(), default=list)

    def __str__(self):
        return f"{self.name}"

    @staticmethod
    def create_groups():
        '''
        Creates the baseline organization groups
        '''
        OrganizationGroup.objects.all().delete()

        baseline_groups = {
            'Arms Control and International Security': ['198000', '197000', '014000'],
            'Civilian Security, Democracy, and Human Rights': ['013000', '033000', '018000', '019000', '030000'],
            'Economic Growth, Energy, and the Environment': ['050000', '025000', '020000'],
            'Management': ['200000', '088000', '280000', '080000', '210000', '170000', '260000', '180000', '016000', '240000', '400000'],
            'Public Diplomacy and Public Affairs': ['230000', '250000', '100000'],
            'Office of the Secretary': ['070000', '060000', '040000', '094000'],
        }

        for name, codes in baseline_groups.items():
            group, _ = OrganizationGroup.objects.get_or_create(name=name)
            group._org_codes = codes
            group.save()

    def update_relationships(self):
        self.organizations.clear()
        self.organizations.add(*list(Organization.objects.filter(code__in=list(self._org_codes))))

    class Meta:
        managed = True
        ordering = ["id"]


class TourOfDuty(StaticRepresentationModel):
    '''
    Represents a tour of duty
    '''

    code = models.TextField(db_index=True, unique=True, null=False, help_text="The tour of duty code")
    long_description = models.TextField(null=False, help_text="Long-format description of the tour of duty")
    short_description = models.TextField(null=False, help_text="Short-format description of the tour of duty")
    months = models.IntegerField(null=False, default=0, help_text="The number of months for this tour of duty")
    is_active = models.BooleanField(default=False)

    _status = models.TextField(null=True)

    def __str__(self):
        return f"{self.long_description}"

    class Meta:
        managed = True
        ordering = ["code"]


class Country(StaticRepresentationModel):
    '''
    Represents a country
    '''

    code = models.TextField(db_index=True, unique=True, null=False, help_text="The unique country code")
    short_code = models.TextField(db_index=True, null=False, help_text="The 2-character country code")
    location_prefix = models.TextField(db_index=True, null=False, help_text="The 2-character location prefix")

    name = models.TextField(help_text="The name of the country")
    short_name = models.TextField(null=True, help_text="The short name of the country")

    obc_id = models.TextField(null=True, help_text="The OBC ID for this country")

    def __str__(self):
        return f"{self.short_name}"

    class Meta:
        managed = True
        ordering = ["code"]


class Location(StaticRepresentationModel):
    '''
    Represents a geographic location
    '''

    code = models.TextField(db_index=True, unique=True, null=False, help_text="The unique location code")

    city = models.TextField(default="", blank=True)
    state = models.TextField(default="", blank=True)
    country = models.ForeignKey(Country, on_delete=models.PROTECT, null=True, related_name="locations", help_text="The country for this location")

    _country = models.TextField(null=True)

    def update_relationships(self):
        # Search for country based on location prefix
        country = Country.objects.filter(location_prefix=self.code[:2])
        if country.count() != 1:
            # Try matching by name
            country = Country.objects.filter(name__iexact=self._country).first()
            if not country:
                # If we still don't have a match, check if the first 2 of the country location code are digits
                if self.code[:2].isdigit():
                    # We're domestic
                    country = Country.objects.filter(code="USA").first()
                else:
                    logging.getLogger(__name__).info(f"Could not find country for {self._country}")
        else:
            country = country.first()

        self.country = country
        self.save()

    def __str__(self):
        string = ", ".join([x for x in [self.city, self.state] if x])
        if self.country and self.country.code != "USA":
            string = f"{self.country.short_name}, " + string
        return string

    class Meta:
        managed = True
        ordering = ["code"]


class Post(StaticRepresentationModel):
    '''
    Represents a post and its related fields
    '''

    location = models.ForeignKey(Location, null=True, on_delete=models.DO_NOTHING, related_name="posts", help_text="The location of the post")

    cost_of_living_adjustment = models.IntegerField(null=False, default=0, help_text="Cost of living adjustment number")
    differential_rate = models.IntegerField(null=False, default=0, help_text="Differential rate number")
    danger_pay = models.IntegerField(null=False, default=0, help_text="Danger pay number")

    rest_relaxation_point = models.TextField(null=False, blank=True, help_text="Rest and relaxation point")

    has_consumable_allowance = models.BooleanField(default=False)
    has_service_needs_differential = models.BooleanField(default=False)

    obc_id = models.TextField(null=True, help_text="The OBC ID for this post")

    tour_of_duty = models.ForeignKey('organization.TourOfDuty', on_delete=models.SET_NULL, null=True, related_name="posts", help_text="The tour of duty")

    _tod_code = models.TextField(null=True)
    _location_code = models.TextField(null=True)

    def update_relationships(self):
        if self._tod_code:
            self.tour_of_duty = TourOfDuty.objects.filter(code=self._tod_code).first()

        if self._location_code:
            self.location = Location.objects.filter(code=self._location_code).first()

        self.create_permissions()

        self.save()

    @property
    def permission_edit_post_capsule_description_codename(self):
        return f"can_edit_post_capsule_description:{self.id}"

    def create_permissions(self):
        '''
        Creates this post's permission set
        '''
        # Create a group for all editor members of a post
        group_name = f"post_editors:{self.id}"
        group, created = Group.objects.get_or_create(name=group_name)

        if created:
            logging.getLogger(__name__).info(f"Created permission group {group_name}")

        # Edit post capsule description action
        permission_codename = self.permission_edit_post_capsule_description_codename
        permission_name = f"Can edit capsule descriptions for post {self.location} ({self.id})"
        content_type = ContentType.objects.get(app_label="position", model="capsuledescription")

        permission, created = Permission.objects.get_or_create(codename=permission_codename,
                                                               name=permission_name,
                                                               content_type=content_type)

        if created:
            logging.getLogger(__name__).info(f"Created permission {permission}")

        # Add the capsule edit permission to the post editors group
        group.permissions.add(permission)

    def __str__(self):
        return f"{self.location}"

    class Meta:
        managed = True
        ordering = ["_location_code"]


@receiver(m2m_changed, sender=Organization.highlighted_positions.through, dispatch_uid="organization_m2m_highlighted")
def assignment_post_save(sender, instance, action, reverse, model, pk_set, **kwargs):
    '''
    This listener updates the highlighted positions highlighted status
    '''
    if action in ["post_add", "post_remove"]:
        for position_id in pk_set:
            pos = talentmap_api.position.models.Position.objects.get(pk=position_id)
            pos.is_highlighted = pos.highlighted_by_org.count() > 0
            pos.save()
