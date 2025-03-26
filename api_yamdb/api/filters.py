from django_filters import FilterSet, CharFilter

from reviews.models import Title


class TitleFilter(FilterSet):
    genre = CharFilter(
        field_name='genre__slug', lookup_expr='iexact')
    category = CharFilter(
        field_name='category__slug', lookup_expr='iexact')
    name = CharFilter(field_name='name', lookup_expr='iexact')

    class Meta:
        model = Title
        fields = ['genre', 'category', 'year', 'name']
