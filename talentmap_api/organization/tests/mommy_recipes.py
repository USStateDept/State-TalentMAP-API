from model_mommy import mommy
from model_mommy.recipe import Recipe, seq, foreign_key
from rest_framework import status

from talentmap_api.organization.models import Organization

# Organization with no parents
orphaned_organization = Recipe(
    Organization,
    code=seq('org_code'),
)
