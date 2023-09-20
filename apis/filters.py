from django_filters import rest_framework as filters
from contracts.models import Contract


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
