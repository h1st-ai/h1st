from typing import Dict, Any

import pandas as pd

from h1st.model.knowledge_model import RuleBasedModel
from h1st.h1flow.h1flow import Graph
from ensemble import MyEnsemble
from oracle import MyOracle
from h1st.h1flow.h1flow import Graph



class MyOracleBuilder:
    def load_data(self) -> Dict:
        path_to_data = ""
        df_data = pd.read_parquet(path_to_data)
        self.feature_list = ['feature_1', 'feature_2']
        return {
            'df_data': df_data[self.feature_list]
        }    

    def build(self, data: Dict, my_knowledge_model: RuleBasedModel) -> Graph:
        df_data = data['df_data']
        # Get K-Model prediction
        y_pred_bool = my_knowledge_model.predict({
            'X': df_data
        })

        # Get Generalizer
        my_gen_modeler = MyGenModeler()
        my_gen_modeler.model_class = MyGeneralizer
        my_generalizer = my_gen_modeler.build({
            "X_train": df_data,
            "y_train": y_pred_bool
        })

        # Get Ensemble
        my_ensemble_modeler = MyEnsembleModeler(
            sub_models=[my_knowledge_model, my_generalizer],
            submodel_predict_input_key='X',
            submodel_predict_output_key='predictions'
        )
        my_ensemble_modeler.model_class = MyEnsemble
        my_ensemble = my_ensemble_modeler.build({
            "X_train": df_data,
            "y_train": y_pred_bool
        })

        my_oracle = MyOracle(
            k_model=my_knowledge_model,
            k_gen=my_generalizer,
            ensemble=my_ensemble
        )
        return my_oracle


class MyOracle(Graph):
    def __init__(self, k_model, k_gen, ensemble):
        super().__init__()
        self.start()
        self.add([k_model, k_gen])
        self.add(ensemble)
        self.end()

