from django.core.serializers.json import DjangoJSONEncoder
from django.http.response import JsonResponse

from inspect import getsource
import json

from ..data.util import \
    load_data_set_pointers_as_json, \
    save_numpy_arrays_and_pandas_dfs_as_data_set_pointers
from .models import H1stModel
from ..trust.models import Decision


def model_exec_on_json_input_data(request, model_uuid, json_input_data):
    model = H1stModel.objects.get(uuid=model_uuid)

    json_input_data = json.loads(json_input_data)

    loaded_json_input_data = load_data_set_pointers_as_json(json_input_data)

    json_output_data = model.predict(loaded_json_input_data)

    saved_json_output_data = \
        save_numpy_arrays_and_pandas_dfs_as_data_set_pointers(json_output_data)

    print(f'OUTPUT: {saved_json_output_data}')

    Decision.objects.create(
        input_data=json_input_data,
        model=model,
        model_code={str(model.uuid): getsource(type(model))},
        output_data=saved_json_output_data)

    return JsonResponse(
            data=saved_json_output_data,
            encoder=DjangoJSONEncoder,
            safe=True,
            json_dumps_params=None)
