from django.contrib.auth.models import User
import rest_framework_filters as filters

from talentmap_api.position.models import Grade, Skill
from talentmap_api.position.filters import GradeFilter, SkillFilter

from talentmap_api.language.filters import QualificationFilter
from talentmap_api.language.models import Qualification

from talentmap_api.user_profile.models import UserProfile

from talentmap_api.organization.filters import CountryFilter
from talentmap_api.organization.models import Country

from talentmap_api.common.filters import ALL_TEXT_LOOKUPS, DATE_LOOKUPS


class UserFilter(filters.FilterSet):

    class Meta:
        model = User
        fields = {
            "first_name": ALL_TEXT_LOOKUPS,
            "last_name": ALL_TEXT_LOOKUPS,
            "username": ALL_TEXT_LOOKUPS
        }


class UserProfileFilter(filters.FilterSet):
    user = filters.RelatedFilter(UserFilter, name='user', queryset=User.objects.all())
    cdo = filters.RelatedFilter('talentmap_api.user_profile.filters.UserProfileFilter', name='cdo', queryset=UserProfile.objects.all())
    grade = filters.RelatedFilter(GradeFilter, name='grade', queryset=Grade.objects.all())
    skill_code = filters.RelatedFilter(SkillFilter, name='skill_code', queryset=Skill.objects.all())
    language_qualifications = filters.RelatedFilter(QualificationFilter, name='language_qualifications', queryset=Qualification.objects.all())
    primary_nationality = filters.RelatedFilter(CountryFilter, name="primary_nationality", queryset=Country.objects.all())
    secondary_nationality = filters.RelatedFilter(CountryFilter, name="primary_nationality", queryset=Country.objects.all())

    class Meta:
        model = UserProfile
        fields = {
            "date_of_birth": DATE_LOOKUPS,
            "phone_number": ALL_TEXT_LOOKUPS,
        }
