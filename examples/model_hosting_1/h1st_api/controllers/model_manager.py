from google.protobuf import text_format
from tensorflow_serving.config import model_server_config_pb2

import requests


class ModelConfig:
    def __init__(self, model_id, model_platform, model_path):
        self.model_id = model_id
        self.model_platform = model_platform
        self.model_path = model_path


class ModelManager:
    @staticmethod
    def get_model_config(model_id):
        model_type = 'tensorflow'
        model_path = ''
        return ModelConfig(model_id, model_type, model_path)

    @staticmethod
    def update_model_config(model_id, model_platform, model_path):
        if model_platform == 'tensorflow':
            TensorFlowModelManager.register_new_model('models.config', model_id, model_path)

class TensorFlowModelManager:
    @staticmethod
    def register_new_model(conf_filepath, name, base_path, model_platform='tensorflow'):
        with open(conf_filepath, 'r+') as f:
            config_ini = f.read()
        model_server_config = model_server_config_pb2.ModelServerConfig()
        model_server_config = text_format.Parse(text=config_ini, message=model_server_config)

        config_list = model_server_config_pb2.ModelConfigList()
        one_config = config_list.config.add()
        one_config.name = name
        one_config.base_path = base_path
        one_config.model_platform = model_platform

        model_server_config.model_config_list.MergeFrom(config_list)
        
        f = open(conf_filepath, "w+")
        f.write(model_server_config.__str__())
        f.close()


class PyTorchModelManager:
    @staticmethod
    def register_new_model(name, workers=1):
        res = requests.post("http://localhost:8081/models?url={name}.mar&initial_workers={workers}".format(name=name, workers=workers))
        return res.json()
