from model_mommy import mommy

from talentmap_api.bidding.models import BidCycle


def tz_aware_bidcycle():
    # Make a bidcycle with proper datetimes for TZ comparison
    return mommy.make(BidCycle,
                      cycle_end_date="2000-01-01T00:00:00+00:00",
                      cycle_deadline_date="1999-01-01T00:00:00+00:00",
                      cycle_start_date="1998-01-01T00:00:00+00:00")
