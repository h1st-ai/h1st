from typing import Dict, Tuple
import requests
from h1st.model.predictive_model import PredictiveModel
import pandas as pd


class RemoteModel(PredictiveModel):
    """
    Class for making inference calls with models served via the Aitomatic Wed API

    Ex:
    model = RemoteModel(API_TOKEN, "MyModelName").load_params()
    predictions = model.predict({'X': MyDataFrame})
    """
    PREDICTION_ENDPOINT = 'https://model-api-dev.platform.aitomatic.com/fuzzy/predict'
    METADATA_ENDPOINT = '://model-api-dev.platform.aitomatic.com/fuzzy/metadata'

    def __init__(self, api_access_token, model_name):
        """
        Initialize remote model

        :param api_access_token: Aitomatic API Access Token
        :param model_name: name of the model being used
        """
        self.model_name = model_name
        self.api_token = api_access_token
        self.headers = {
            'API-ACCESS-TOKEN': self.api_access_token,
            'Content-Type': 'application/json'
        }

    def predict(self, input_data: Dict) -> Dict:
        """
        Logic to generate prediction from data

        :params input_data: input data for prediction, dictionary with data under key 'X'
        :return: a dictionary with key `predictions` containing the predictions
        """
        # Convert data to JSON safe dict
        json_data, types_dict = convert_data_to_json(input_data)

        # Create web request dicts
        request_data = {
            'model_name': self.model_name,
            'version': self.version,
            'input_data': json_data
        }

        # Convert data to json str (NpEncoder allows numpy array conversion)
        request_data = json.dumps(request_data, cls=NpEncoder)

        # Make web request
        resp = requests.post(
            self.PREDICTION_ENDPOINT,
            headers=self.headers,
            data=request_data
        )

        # Handle request errors
        if resp.status_code != 200:
            err = f'{resp.status_code}: {resp.content}'
            raise ConnectionError(err)

        resp_content = json.loads(resp.content)

        # Convert response back to correct types
        # predictions format to match input_data['X'] format/types
        predictions = convert_json_to_data(resp_content.pop('predictions'), types_dict)
        resp_content['predictions'] = predictions
        return resp_content

    def process(self, input_data: Dict) -> Dict:
        """
        Implement logic to generate prediction from data
        """
        return self.predict(input_data=input_data)

    def persist(self, version: str) -> str:
        raise NotImplementedError()

    def load_params(self, *args, **kwargs) -> 'RemoteModel':
        return self.load(*args, **kwargs)

    def load(self, version: str='latest') -> 'RemoteModel':
        """
        load model parameters for usage

        :param version: (optional) version of the model to load, defaults to
        latest
        """
        self.version = version

        # TODO: Make API call to get model stats & metrics, uncomment below
        # when API implemented

        # resp = requests.get(
        #     self.METADATA_ENDPOINT,
        #     headers=self.headers,
        #     params={'model_name': self.model_name, 'version': version},
        # )

        # # Handle request errors
        # if resp.status_code != 200:
        #     err = f'{resp.status_code}: {resp.content}'
        #     raise ConnectionError(err)

        # resp_data = json.loads(resp.content)
        # self.stats = resp_data['stats']
        # self.metrics = resp_data['metrics']
        return self

def convert_data_to_json(input_data: Dict) -> Tuple[Dict, Dict]:
    """
    Converts input data to json str for web request. 
    Supports dict, pandas DataFrame, pandas Series and numpy arrays
    """
    out_data = {}
    types_dict = {}
    for k,v in input_data.items():
        types_dict[k] = type(v)
        if isinstance(v, (pd.DataFrame, pd.Series)):
            out_data[k] = json.loads(v.to_json())
        elif isinstance(v, dict):
            # no changes needed
            out_data[k] = v
        elif isinstance(v, np.ndarray):
            # Convert later using JSONEncoder NpEncoder
            out_data[k] = v
        else:
            out_data[k] = v

        if k.lower() in ['x', 'x_train', 'x_test']:
            types_dict['predictions'] = type(v)

    if 'predictions' not in types_dict.keys():
        types_dict['predictions'] = pd.DataFrame

    #out_json = json.dumps(out_data, cls=NpEncoder)
    return out_data, types_dict

def convert_json_to_data(json_data: Dict, types_dict: Dict) -> Dict:
    """
    converts json data input pandas Dataframe or pandas Series or numpy array
    depending on the types_dict generated when converting the input_data into
    json
    """
    out_data = {}
    for k,v in json.loads(json_data).items():
        goal_type = types_dict.get(k, pd.DataFrame)
        if goal_type == pd.DataFrame or goal_type == pd.Series:
            out_data[k] = goal_type(v)
        elif goal_type == np.ndarray:
            out_data[k] = np.array(v, dtype='O')
        else:
            out_data[k] = v

    return out_data

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)

