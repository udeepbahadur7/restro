import django_filters
from django.http.response import Http404
from django_filters.widgets import RangeWidget

from wifiportal.models import Customer
from dashboard.forms import DateInput


class CustomDateTimeRangeWidget(RangeWidget):
    def __init__(self, attrs=None):
        widgets = (DateInput, DateInput)
        super(RangeWidget, self).__init__(widgets, attrs)


class CustomerFilter(django_filters.FilterSet):
    entry_timestamp = django_filters.DateTimeFromToRangeFilter(
        label='Customer Date Filter',
        widget=CustomDateTimeRangeWidget()
    )

    class Meta:
        model = Customer
        fields = ['entry_timestamp']

    @property
    def qs(self):
        parent_qs = super(CustomerFilter, self).qs
        if not self.request:
            raise ValueError('request object is required. Pass request as kwargs when initializing Filter.')

        if self.request.user.has_perm('alter_all_customer_data'):
            return parent_qs

        if not hasattr(self.request.user, 'organization'):
            raise Http404('User manages no organization!!!')

        organization = self.request.user.organization
        return parent_qs.filter(organization=organization.id)
