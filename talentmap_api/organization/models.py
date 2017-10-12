from django.db import models
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

import logging


class Organization(models.Model):
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
        # Array of regional codes
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
        else:
            self.is_regional = False

        if self._parent_bureau_code:
            if self.code != self._parent_bureau_code:
                bureau = Organization.objects.filter(code=self._parent_bureau_code)
                if bureau.count() != 1:
                    logging.getLogger('console').warn(f"While setting organization relationships, got {bureau.count()} values for bureau code {self._parent_bureau_code}")
                else:
                    self.bureau_organization = bureau.first()
            else:
                self.is_bureau = True
        if self._parent_organization_code:
            org = Organization.objects.filter(code=self._parent_organization_code)
            if org.count() != 1:
                logging.getLogger('console').warn(f"While setting organization relationships, got {org.count()} values for org code {self._parent_organization_code}")
            else:
                self.parent_organization = org.first()

        if self._location_code:
            loc = Location.objects.filter(code=self._location_code)
            if loc.count() != 1:
                logging.getLogger('console').warn(f"While setting organization location, got {loc.count()} values for location code {self._location_code}")
            else:
                self.location = loc.first()

        self.save()

        if self.is_bureau:
            self.create_permissions()

    def create_permissions(self):
        '''
        Creates this organization's permission set
        '''
        # Create a group for AOs for this bureau
        group_name = f"bureau_ao_{self.code}"
        group = Group.objects.get_or_create(name=group_name)

        if group[1]:
            logging.getLogger('console').info(f"Created permission group {group_name}")

        group = group[0]

        # Highlight action
        permission_codename = f"can_highlight_positions_{self.code}"
        permission_name = f"Can highlight positions for {self.short_description} ({self.code})"
        content_type = ContentType.objects.get_for_model(type(self))

        permission = Permission.objects.get_or_create(codename=permission_codename,
                                                      name=permission_name,
                                                      content_type=content_type)

        if permission[1]:
            logging.getLogger('console').info(f"Created permission {permission[0]}")

        # Add the highlight permission to the AO group
        group.permissions.add(permission[0])

    def __str__(self):
        return f"{self.long_description} ({self.short_description})"

    class Meta:
        managed = True
        ordering = ["code"]


class TourOfDuty(models.Model):
    '''
    Represents a tour of duty
    '''

    code = models.TextField(db_index=True, unique=True, null=False, help_text="The tour of duty code")
    long_description = models.TextField(null=False, help_text="Long-format description of the tour of duty")
    short_description = models.TextField(null=False, help_text="Short-format description of the tour of duty")
    months = models.IntegerField(null=False, default=0, help_text="The number of months for this tour of duty")

    def __str__(self):
        return f"{self.long_description}"

    class Meta:
        managed = True
        ordering = ["code"]


class Country(models.Model):
    '''
    Represents a country
    '''

    code = models.TextField(db_index=True, unique=True, null=False, help_text="The unique country code")
    short_code = models.TextField(db_index=True, unique=True, null=False, help_text="The unique 2-character country code")

    name = models.TextField(help_text="The name of the region")
    short_name = models.TextField(null=True, help_text="The short name of the region")

    is_current = models.BooleanField(default=True, help_text="Boolean indicator if this country is current")
    is_country = models.BooleanField(default=False, help_text="Boolean indicator if this region is a country")
    is_territory = models.BooleanField(default=False, help_text="Boolean indicator if this region is a territory")

    def __str__(self):
        return f"{self.name}"

    class Meta:
        managed = True
        ordering = ["code"]


class Location(models.Model):
    '''
    Represents a geographic location
    '''

    code = models.TextField(db_index=True, unique=True, null=False, help_text="The unique location code")

    city = models.TextField(default="", blank=True)
    state = models.TextField(default="", blank=True)
    country = models.ForeignKey(Country, on_delete=models.PROTECT, null=True, related_name="locations", help_text="The country for this location")

    def update_relationships(self):
        country = Country.objects.filter(short_code=self.code[:2]).first()
        # If we don't have a matching country for the location code, but the code we tried is
        # a digit, then we are in the USA
        if not country and self.code[:2].isdigit():
            country = Country.objects.filter(code="USA").first()
        else:
            logging.getLogger('console').info(f"Could not find country for code {self.code}")

        self.country = country
        self.save()

    def __str__(self):
        return ", ".join([x for x in [self.city, self.state] if x])

    class Meta:
        managed = True
        ordering = ["code"]


class Post(models.Model):
    '''
    Represents a post and its related fields
    '''

    location = models.ForeignKey(Location, null=True, related_name="posts", help_text="The location of the post")

    cost_of_living_adjustment = models.IntegerField(null=False, default=0, help_text="Cost of living adjustment number")
    differential_rate = models.IntegerField(null=False, default=0, help_text="Differential rate number")
    danger_pay = models.IntegerField(null=False, default=0, help_text="Danger pay number")

    rest_relaxation_point = models.TextField(null=False, blank=True, help_text="Rest and relaxation point")

    has_consumable_allowance = models.BooleanField(default=False)
    has_service_needs_differential = models.BooleanField(default=False)

    tour_of_duty = models.ForeignKey('organization.TourOfDuty', on_delete=models.SET_NULL, null=True, related_name="posts", help_text="The tour of duty")

    _tod_code = models.TextField(null=True)
    _location_code = models.TextField(null=True)

    def update_relationships(self):
        if self._tod_code:
            self.tour_of_duty = TourOfDuty.objects.filter(code=self._tod_code).first()

        if self._location_code:
            self.location = Location.objects.filter(code=self._location_code).first()

        self.save()

    def __str__(self):
        return f"{self.location}"

    class Meta:
        managed = True
        ordering = ["_location_code"]
