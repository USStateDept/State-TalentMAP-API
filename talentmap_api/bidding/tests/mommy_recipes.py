from model_mommy import mommy
from model_mommy.recipe import Recipe, foreign_key

from talentmap_api.bidding.models import BidCycle, CyclePosition

bidcycle = Recipe(
    BidCycle,
    active=True
)

cycleposition = Recipe(
    CyclePosition,
    bidcycle=foreign_key('bidcycle'),
)

def tz_aware_bidcycle():
    # Make a bidcycle with proper datetimes for TZ comparison
    return mommy.make(BidCycle,
                      cycle_end_date="2000-01-01T00:00:00+00:00",
                      cycle_deadline_date="1999-01-01T00:00:00+00:00",
                      cycle_start_date="1998-01-01T00:00:00+00:00")
