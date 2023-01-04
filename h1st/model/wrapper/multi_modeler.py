from typing import Union
from h1st.model.wrapper.multi_model import MultiModel
from h1st.model.modeler import Modeler
from joblib import Parallel, delayed

class MultiModeler(Modeler):
    model_class = MultiModel

    def __init__(self):
        super().__init__()
        self.stats = {}

    def build_model(self, prepared_data: dict,
                    modelers: Union[dict, list] = [],
                    parallel=False):
        """prepared data has keys necessary for modelers build_model function.
        If modelers is a dict, they keys should be unique names for the
        resultant models. If it is a list, the modeler should have model_name
        in stats dict or a name will be automatically assigned"""
        if isinstance(modelers, list):
            for i, m in enumerate(modelers):
                if m.stats.get('model_name') is None:
                    m.model_name = f'{m.__class__.__name__}-{i}'
        elif isinstance(modelers, dict):
            new_ = []
            for k,v in modelers.items():
                v.model_name = k
                new_.append(v)

            modelers = new_

        model = self.model_class()
        if parallel:
            submodels = Parallel(n_jobs=-2, verbose=10)(
                delayed(x.build_model)(prepared_data) for x in modelers
            )
            for submodel in submodels:
                model.add_model(submodel, name=submodel.stats.get('model_name'))

        else:
            for modeler in modelers:
                submodel = modeler.build_model(prepared_data)
                model.add_model(submodel, name=submodel.stats.get('model_name'))

        model.metrics = self.evaluate_model(prepared_data, model)
        model.stats = self.stats.copy()
        return model

    def evaluate_model(self, prepared_data, model):
        return model.get_submodel_model_metrics()

