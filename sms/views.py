from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView

from sms.forms import CustomerFilter
from wifiportal.models import Customer


@method_decorator(staff_member_required, 'dispatch')
class CustomerPreview(ListView):
    model = Customer
    paginate_by = 10
    template_name = "sms/customer_preview.html"

    def get_context_data(self, **kwargs):
        context = super(CustomerPreview, self).get_context_data(**kwargs)
        customer_filter = CustomerFilter(self.request.GET, request=self.request)
        context.update(
            customer_count=customer_filter.qs.count(),
            is_popup=True

        )
        return context

    def get_queryset(self):
        customer_filter = CustomerFilter(self.request.GET, request=self.request)
        return customer_filter.qs