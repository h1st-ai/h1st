from django_model_query_graphs import ModelQueryGraph

from ...models import DataSet


DATA_SET_REST_API_QUERY_GRAPH = \
    ModelQueryGraph(
        DataSet,
        'uuid',
        'created',
        'modified')

DATA_SET_REST_API_QUERY_SET = DATA_SET_REST_API_QUERY_GRAPH.query_set()
