from rest_framework.authentication import \
    BasicAuthentication, \
    RemoteUserAuthentication, \
    SessionAuthentication, \
    TokenAuthentication
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import CoreJSONRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from rest_framework.filters import OrderingFilter
from rest_framework_filters.backends import \
    ComplexFilterBackend, \
    RestFrameworkFilterBackend

from silk.profiling.profiler import silk_profile

from ...models import DataSet
from ...util import load_data_set_pointers_as_json
from .filters import DataSetFilter
from .queries import DATA_SET_REST_API_QUERY_SET
from .serializers import DataSetSerializer


class DataSetViewSet(ModelViewSet):
    queryset = DATA_SET_REST_API_QUERY_SET

    serializer_class = DataSetSerializer

    authentication_classes = \
        BasicAuthentication, \
        RemoteUserAuthentication, \
        SessionAuthentication, \
        TokenAuthentication

    permission_classes = IsAuthenticated,

    filter_class = DataSetFilter

    filter_backends = \
        OrderingFilter, \
        ComplexFilterBackend, \
        RestFrameworkFilterBackend

    ordering_fields = \
        'uuid', \
        'created', \
        'modified'

    ordering = '-modified'

    pagination_class = LimitOffsetPagination

    parser_classes = JSONParser,

    renderer_classes = \
        CoreJSONRenderer, \
        JSONRenderer

    @silk_profile(name=f'{__module__}: {DataSet._meta.verbose_name_plural}')
    def list(self, *args, **kwargs):
        return super().list(*args, **kwargs)

    @silk_profile(name=f'{__module__}: {DataSet._meta.verbose_name}')
    def retrieve(self, *args, **kwargs):
        return super().retrieve(*args, **kwargs)


class DataQueryAPIView(APIView):
    authentication_classes = \
        BasicAuthentication, \
        RemoteUserAuthentication, \
        SessionAuthentication, \
        TokenAuthentication

    permission_classes = IsAuthenticated,

    parser_classes = JSONParser,

    def post(self, request, *args, **kwargs):
        return Response(
                data=load_data_set_pointers_as_json(request.data),
                status=None,
                template_name=None,
                headers=None,
                exception=False,
                content_type=None)
