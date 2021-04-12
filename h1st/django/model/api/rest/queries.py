from django_model_query_graphs import ModelQueryGraph

from ...models import Model


MODEL_REST_API_QUERY_GRAPH = \
    ModelQueryGraph(
        Model,
        'uuid',
        'created',
        'modified')

MODEL_REST_API_QUERY_SET = MODEL_REST_API_QUERY_GRAPH.query_set()
