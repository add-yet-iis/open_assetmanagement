'''This file contains django filters for the django models
'''
from .models import Device
import django_filters
from django_filters import CharFilter


class DeviceFilter(django_filters.FilterSet):
    '''This Class is used to filter the Device Names in a queryset

    '''
    device_name = CharFilter(field_name='device_name', lookup_expr='icontains')

    class Meta:
        model = Device
        fields = []
