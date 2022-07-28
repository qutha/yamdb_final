import django_filters
from django_filters import filters

from .models import Title


class TitleFilter(django_filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='contains')
    year = filters.NumberFilter(field_name='year')
    genre = filters.CharFilter(field_name='genre__slug')
    category = filters.CharFilter(field_name='category__slug')

    class Meta:
        model = Title
        fields = ('name', 'year', 'genre', 'category',)
