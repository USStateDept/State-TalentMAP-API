from model_mommy import mommy
from model_mommy.recipe import Recipe, seq, foreign_key
from rest_framework import status

from talentmap_api.organization.models import Organization, TourOfDuty, Post

# Organization with no parents
orphaned_organization = Recipe(
    Organization,
    code=seq('org_code'),
)

tour_of_duty = Recipe(
    TourOfDuty,
    code=seq('tod_code')
)

post = Recipe(
    Post,
    code=seq('post_code'),
    tour_of_duty=foreign_key('tour_of_duty')
)
