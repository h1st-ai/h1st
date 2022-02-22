import os
import tarfile
import tempfile
import logging
import importlib
from distutils import dir_util
from typing import Any

import yaml
import ulid
from h1st.model.ml_modeler import BaseModelType, MLModeler
from h1st.model.modelable import Modelable
from h1st.model.modeler import Modeler

from h1st.model.repository.storage.s3 import S3Storage
from h1st.model.repository.storage.local import LocalStorage

SEP = "::"
logger = logging.getLogger(__name__)


class ModelSerDes:
    STATS_PATH = 'stats.joblib'
    METRICS_PATH = 'metrics.joblib'
    METAINFO_FILE = 'METAINFO.yaml'

    def _serialize_dict(self, d, path, dict_file):
        import joblib
        joblib.dump(d, path + '/%s' % dict_file)

    def _deserialize_dict(self, path, dict_file):
        import joblib
        return joblib.load(path + '/%s' % dict_file)

    """
    # Deprecated
    def _get_model_type(self, model):
        import tensorflow
        import sklearn

        if isinstance(model, sklearn.base.BaseEstimator):
            return 'sklearn'
        if isinstance(model, tensorflow.keras.Model):
            return 'tensorflow-keras'
        if model is None:
            return 'custom'
    """

    def _serialize_base_model(self, base_model, path, model_name='model'):
        """
        :return: model_type: BaseModelType, model_path: str
        """
        model_type = MLModeler.get_base_model_type(base_model)

        if model_type == BaseModelType.SCIKITLEARN:
            # This is a sklearn model
            import joblib
            model_path = '%s.joblib' % model_name
            joblib.dump(base_model, path + '/%s' % model_path)

        elif model_type == BaseModelType.TENSORFLOW:
            model_path = model_name
            os.makedirs(path + '/%s' % model_path, exist_ok=True)
            base_model.save_weights(path + '/%s/weights' % model_path)

        elif model_type == BaseModelType.PYTORCH:
            model_path = model_name  # XXX

        else:
            raise ValueError('Unsupported model!!!')

        return model_type, model_path

    def _deserialize_base_model(self, dirname, base_model_class, filename) -> Any:
        """
        :return: base_model
        """
        if not base_model_class:
            return None
        
        base_model_type = MLModeler.get_base_model_type(base_model_class)

        if base_model_type == BaseModelType.SCIKITLEARN:
            # This is a sklearn model
            import joblib
            base_model = joblib.load(dirname + '/%s' % filename)
            # print(str(type(model)))
        elif base_model_type == BaseModelType.TENSORFLOW:
            base_model = base_model_class()
            base_model.load_weights(dirname + '/%s/weights' % filename).expect_partial()
        else:
            base_model = None

        return base_model

    def serialize(self, model_object: Modelable, to_path):
        """
        Serialize a H1ST model's model property to disk.

        :param model_object: H1ST Modelable
        :param to_path: path to save models to
        """
        from h1st.model.ml_model import MLModel
        from h1st.model.rule_based_model import RuleBasedModel

        meta_info = {}

        if model_object.metrics:
            logger.info('Saving metrics property...')
            meta_info['metrics'] = self.METRICS_PATH
            self._serialize_dict(model_object.metrics, to_path, self.METRICS_PATH)

        if model_object.stats is not None:
            logger.info('Saving stats property...')
            meta_info['stats'] = self.STATS_PATH
            self._serialize_dict(model_object.stats, to_path, self.STATS_PATH)

        if isinstance(model_object, MLModel):
            if model_object.base_model:
                logger.info('Saving model property...')
                if type(model_object.base_model) == list:
                    meta_info['models'] = []
                    for i, model_object in enumerate(model_object.base_model):
                        model_type, model_path = self._serialize_base_model(model_object, to_path, 'model_%d' % i)
                        meta_info['models'].append({'model_type': model_type, 'model_path': model_path})
                elif type(model_object.base_model) == dict:
                    meta_info['models'] = {}
                    for k, model_object in model_object.base_model.items():
                        model_type, model_path = self._serialize_base_model(model_object, to_path, 'model_%s' % k)
                        meta_info['models'][k] = {'model_type': model_type, 'model_path': model_path}
                else:
                    # this is a single model
                    model_type, model_path = self._serialize_base_model(model_object.base_model, to_path)
                    meta_info['models'] = [{'model_type': model_type, 'model_path': model_path}]
            else:
                logger.error('.base_model was not assigned.')

        elif not isinstance(model_object, RuleBasedModel):
            pass
        elif hasattr(model_object, 'base_model'):
            logger.warning('Your .base_model will not be persisted. If you want to persist your .base_model, \
                            must inherit from h1st.MLModel instead of h1st.Model.')

        if len(meta_info) == 0:
            logger.info('Model persistence currently supports only stats, model and metrics properties.')
            logger.info(
                'Make sure you store stastistic in stats property, models in model property and model metrics in metrics one.')

        with open(os.path.join(to_path, self.METAINFO_FILE), 'w') as file:
            yaml.dump(meta_info, file)

    def deserialize(self, model_class, path) -> Modelable:
        """
        Populate a H1ST model's model property with saved atomic models.

        :param model_class: class of model to be deserialized
        :param path: path to model folder
        :return: the model object that was instantiated
        :rtype: Modelable
        """
        
        # Instantiate a model oject
        model_object = model_class.get_modeler().build_model() # TODO: verify

        # Read METAINFO
        with open(os.path.join(path, self.METAINFO_FILE), 'r') as file:
            meta_info = yaml.load(file, Loader=yaml.Loader)

        if 'metrics' in meta_info.keys():
            model_object.metrics = self._deserialize_dict(path, self.METRICS_PATH)

        if 'stats' in meta_info.keys():
            model_object.stats = self._deserialize_dict(path, self.STATS_PATH)

        if 'models' in meta_info.keys():
            model_infos = meta_info['models']
            orig_base_model = model_object.base_model  # original base model object from Model class
            if type(model_infos) == list:
                if len(model_infos) == 1:
                    # Single model
                    model_info = model_infos[0]
                    # print(model_info)
                    model_type = model_info['model_type']
                    model_path = model_info['model_path']
                    model_object.base_model = self._deserialize_base_model(orig_base_model, path, model_type, model_path)
                else:
                    # A list of models
                    model_object.base_model = []
                    orig_base_model = orig_base_model or [None for _ in range(len(model_infos))]
                    for i, model_info in enumerate(model_infos):
                        model_type = model_info['model_type']
                        model_path = model_info['model_path']
                        model_object.base_model.append(
                            self._deserialize_base_model(orig_base_model[i], path, model_type, model_path))

            elif type(model_infos) == dict:
                # A dict of models
                model_object.base_model = {}
                orig_base_model = orig_base_model or {k: None for k in model_infos.keys()}
                for model_name, model_info in model_infos.items():
                    model_type = model_info['model_type']
                    model_path = model_info['model_path']
                    model_object.base_model[model_name] = self._deserialize_base_model(orig_base_model[model_name], path, model_type, model_path)
            else:
                raise ValueError('Not a valid H1ST Model METAINFO file!')

        return model_object
