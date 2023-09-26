from django.utils import timezone
from django_filters import rest_framework as filters

from contracts.models import Contract
from events.models import Event


class ContractFilter(filters.FilterSet):
    """Custom filter adding is_signed boolean filter
    and min_payment_due filter witch exclude contracts with payment_due is 0.0."""

    min_payment_due = filters.NumberFilter(field_name="payment_due", lookup_expr="gt")

    class Meta:
        model = Contract
        fields = ["is_signed", "min_payment_due"]

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        min_payment_due = self.request.query_params.get("min_payment_due__gt")
        if min_payment_due is not None:
            queryset = queryset.exclude(payment_due=0.0)
        return queryset


class ExcludePastDateOrderingFilter(filters.OrderingFilter):
    """Exclude past dates if order field is start_date."""

    def filter(self, qs, value):
        if value and value[0] == "start_date":
            now = timezone.now()
            return qs.filter(start_date__gte=now).order_by(*value)
        return super().filter(qs, value)


class EventFilter(filters.FilterSet):
    order_by = ExcludePastDateOrderingFilter(
        fields=(("start_date", "start_date"),),
        field_labels={
            "start_date": "Classement par prochaines dates",
        },
    )
    null_support_contact = filters.BooleanFilter(
        field_name="support_contact", lookup_expr="isnull"
    )
    support_contact_first_name = filters.CharFilter(
        field_name="support_contact__first_name", lookup_expr="icontains"
    )
    support_contact_last_name = filters.CharFilter(
        field_name="support_contact__last_name", lookup_expr="icontains"
    )

    class Meta:
        model = Event
        fields = [
            "null_support_contact",
            "support_contact_first_name",
            "support_contact_last_name",
        ]
