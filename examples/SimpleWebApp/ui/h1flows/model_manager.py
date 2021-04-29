from google.protobuf import text_format
from tensorflow_serving.config import model_server_config_pb2


class TensorFlowModelManager:
    @staticmethod
    def update_model_configs(conf_filepath, name, base_path, model_platform='tensorflow'):
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
