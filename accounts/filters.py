from attr import field
import django_filters
from django_filters import DateFilter, CharFilter

from .models import *

class OrderFilter(django_filters.FilterSet):

    # Change default fields
    note = CharFilter(field_name='note', lookup_expr='icontains')

    # Create custom fields
    custom_date_start = DateFilter(field_name = 'date_created', lookup_expr = 'gte')
    custom_date_end = DateFilter(field_name = 'date_created', lookup_expr = 'lte')

    class Meta:
        model = Order
        fields = '__all__'
        exclude = ['customer', 'date_created']