from django_filters.filters import OrderingFilter
from rest_framework_filters.filterset import FilterSet

from ...models import DataSet


class DataSetFilter(FilterSet):
    class Meta:
        model = DataSet

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
