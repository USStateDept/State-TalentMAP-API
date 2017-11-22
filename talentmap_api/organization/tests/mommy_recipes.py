from model_mommy.recipe import Recipe, seq, foreign_key

from talentmap_api.organization.models import Organization, TourOfDuty, Post, Location, Country

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
    tour_of_duty=foreign_key('tour_of_duty')
)

country = Recipe(
    Country,
    code=seq('country_code')
)

location = Recipe(
    Location,
    code=seq('location_code'),
    country=foreign_key('country')
)
