import uuid
import pandas as pd
from h1st.model.predictive_model import PredictiveModel


class MultiModel(PredictiveModel):
    name = 'multi_model'
    data_key = 'X'
    output_key = 'predictions'

    def __init__(self):
        super().__init__()
        self.models = {}
        self.stats = {}

    def predict(self, data: dict) -> dict:

        X = data[self.data_key]
        all_pred = []
        for k, v in self.models.items():
            pred_key = getattr(v, 'output_key', 'predictions')
            pred: pd.DataFrame = v.predict({v.data_key: X})[pred_key]

            all_pred.append(
                pd.Series(pred.squeeze(), name=f'{k}')
            )

        out = {self.output_key: pd.concat(all_pred, axis=1)}
        return out

    def persist(self, version=None):
        models = self.models
        model_info = self.model_info
        for k, v in models.items():
            model_version = v.persist()
            model_info[k]['version'] = model_version
            model_info[k]['model_class'] = v.__class__

        self.stats['model_info'] = model_info
        version = super().persist(version)
        return version

    def load(self, version=None):
        super().load(version)

        model_info = self.stats['model_info']
        models = {}
        for k, v in model_info.items():
            models[k] = v['model_class']().load(v['version'])

        self.models = models
        return self

    def _update_model_info(self):
        model_info = self.stats.get('model_info')
        if model_info is None:
            model_info = {}

        for k, v in self.models.items():
            info = {
                'model_name': k,
                'model_type': v.name,
                'metrics': v.metrics,
                'stats': v.stats
            }
            if k in model_info.keys():
                model_info[k].update(info)
            else:
                model_info[k] = info

        self.stats['model_info'] = model_info

    @property
    def model_info(self):
        self._update_model_info()
        return self.stats['model_info']

    def add_model(self, model, name=None):
        if name is None:
            name = model.name + '-' + uuid.uuid4().hex

        self.models[name] = model
        self._update_model_info()

    def get_submodel_model_metrics(self):
        metrics = {k: getattr(v, 'metrics', {})
                   for k, v in self.models.items()}
        return metrics

