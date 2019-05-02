from django_filters import rest_framework as filters
from .models import UserProfile

class UserProfileFilterSet(filters.FilterSet):
    gender = filters.ChoiceFilter(choices = UserProfile.GENDER_CHOICE,)
    joinDate = filters.DateFromToRangeFilter()
    dateOfBirth = filters.DateFilter()

    class Meta:
        model = UserProfile
        fields = ('gender', 'joinDate', 'dateOfBirth')
