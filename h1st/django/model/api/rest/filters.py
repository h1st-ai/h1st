from django_filters.filters import OrderingFilter
from rest_framework_filters.filterset import FilterSet

from ...models import Model


class ModelFilter(FilterSet):
    class Meta:
        model = Model

        fields = dict(
            uuid=(
                'exact',
                'in',
                'contains', 'icontains',
                'startswith', 'istartswith', 'endswith', 'iendswith',
                'regex', 'iregex'
            ),

            created=(
                'exact',
                'gt', 'gte', 'lt', 'lte',
                'in',
                'contains', 'icontains',
                'startswith', 'istartswith', 'endswith', 'iendswith',
                'range',
                'regex', 'iregex'
            ),

            modified=(
                'exact',
                'gt', 'gte', 'lt', 'lte',
                'in',
                'contains', 'icontains',
                'startswith', 'istartswith', 'endswith', 'iendswith',
                'range',
                'regex', 'iregex'
            )
        )

    order_by = \
        OrderingFilter(
            fields=(
                'created',
                'modified'
            )
        )
