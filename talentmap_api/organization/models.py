from django.db import models

import logging


class Organization(models.Model):
    '''
    The organization model represents a DoS organization, such as bureaus
    '''

    code = models.TextField(db_index=True, unique=True, null=False, help_text="The organization code")
    long_description = models.TextField(null=False, help_text="Long-format description of the organization")
    short_description = models.TextField(null=False, help_text="Short-format description of the organization")

    # An organization is a Bureau if its bureau code is the same as its code
    is_bureau = models.BooleanField(default=False, help_text="Boolean indicator if this organization is a bureau")

    parent_organization = models.ForeignKey('organization.Organization', on_delete=models.SET_NULL, null=True, related_name="organizion_children", help_text="The parent organization of this organization")
    bureau_organization = models.ForeignKey('organization.Organization', on_delete=models.SET_NULL, null=True, related_name="bureau_children", help_text="The parent Bureau for this organization")

    # These fields are used during loading to preserve source coded data, before the FK relationships are set
    # These also preserve the data should the FK items be deleted
    _parent_organization_code = models.TextField(null=True, help_text="Organization Code of the parent Organization")
    _parent_bureau_code = models.TextField(null=True, help_text="Bureau Code of the parent parent Bureau")

    def update_relationships(self):
        '''
        Update the organization relationships, using the codes stored in the _parent fields.
        '''
        if self._parent_bureau_code:
            if self.code != self._parent_bureau_code:
                bureau = Organization.objects.filter(code=self._parent_bureau_code)
                if bureau.count() != 1:
                    logging.getLogger('console').warn("While setting organization relationships, got {} values for bureau code {}".format(bureau.count(), self._parent_bureau_code))
                else:
                    self.bureau_organization = bureau.first()
            else:
                self.is_bureau = True
        if self._parent_organization_code:
            org = Organization.objects.filter(code=self._parent_organization_code)
            if org.count() != 1:
                logging.getLogger('console').warn("While setting organization relationships, got {} values for org code {}".format(org.count(), self._parent_organization_code))
            else:
                self.parent_organization = org.first()

        self.save()

    def __str__(self):
        return "{} ({})".format(self.long_description, self.short_description)
