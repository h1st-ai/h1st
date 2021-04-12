from rest_framework.serializers import ModelSerializer, SerializerMethodField

from ...models import DataSet


class DataSetSerializer(ModelSerializer):
    description = SerializerMethodField(method_name='get_description')

    json = SerializerMethodField(method_name='get_json')

    class Meta:
        model = DataSet

        fields = \
            'description', \
            'uuid', \
            'json', \
            'created', \
            'modified'

    def get_description(self, obj):
        return str(obj)

    def get_json(self, obj):
        return obj.json
