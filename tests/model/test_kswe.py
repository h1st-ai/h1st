import os
import tempfile
import sys
from typing import Any, Dict

import pandas as pd
from sklearn import datasets
from sklearn.linear_model import LogisticRegression
from sklearn import metrics as sk_metrics
from sklearn.model_selection import train_test_split

from h1st.model.model import Model
from h1st.model.ml_model import MLModel
from h1st.model.ml_modeler import MLModeler
from h1st.model.rule_based_modeler import RuleBasedModeler
from h1st.model.kswe import KSWE, KSWEModeler, MaxSegmentationModeler, MajorityVotingEnsemble


class MySubModel(MLModel):
    def predict(self, input_data: Dict) -> Dict:
        y = self.base_model.predict(input_data['X'])
        return {'predictions': y}


class MySubModelModeler(MLModeler):
    def __init__(self, model_class=MySubModel):
        self.model_class = model_class
        self.stats = {}
    
    def evaluate_model(self, data: Dict, model: MLModel) -> Dict:
        # super().evaluate_model(data, model)
        if 'X_test' not in data:
            print('No test data found. evaluating training results')
            X, y_true = data['X_train'], data['y_train']
        else:
            X, y_true = data['X_test'], data['y_test']
        y_pred = pd.Series(model.predict({'X': X})['predictions'])
        return {'r2_score': sk_metrics.r2_score(y_true, y_pred)}

    def train_base_model(self, data: Dict[str, Any]) -> Any:
        X, y = data['X_train'], data['y_train']
        model = LogisticRegression(random_state=0)
        model.fit(X, y)
        return model

def load_data():
        df_raw = datasets.load_iris(as_frame=True).frame
        df_raw.columns = ['sepal_length','sepal_width','petal_length','petal_width', 'species']
        df_raw['sepal_size'] = df_raw['sepal_length'] * df_raw['sepal_width']
        df_raw['sepal_aspect_ratio'] =  df_raw['sepal_width'] / df_raw['sepal_length'] 
        X_cols = list(df_raw.columns)
        X_cols.remove('species')
        X_train, X_test, y_train, y_test = train_test_split(
            df_raw[X_cols], df_raw['species'], test_size=0.4, random_state=1)
        return {
            'X_train': X_train, 
            'y_train': y_train, 
            'X_test': X_test,
            'y_test': y_test,
        }

class TestKSWE:
    def test_max_segmentor_n_sklearn_sub_model_n_rule_based_ensemble(self):
        data = load_data()

        segmentation_config = {
            'min_segment_size': 10,
            'features': ['sepal_size', 'sepal_aspect_ratio'],
            'custom_bins':{
                'sepal_size': [[(0, 18.5)], [(18.5,50)]],
                'sepal_aspect_ratio': [[(0, 0.65)], [(0.65, 1)]],
            },
            'n_bins':{
                'sepal_aspect_ratio': 4
            }
        }
        kswe_modeler = KSWEModeler()
        kswe = kswe_modeler.build_model(
            input_data=data,
            segmentation_config=segmentation_config, 
            sub_model_modeler=MySubModelModeler()
        )

        def test_kswe(kswe, data):
            X, y_true = data['X_test'], data['y_test']
            y_pred = pd.Series(kswe.predict({'X': X})['predictions'])
            return {'r2_score': sk_metrics.r2_score(y_true, y_pred)}  

        with tempfile.TemporaryDirectory() as path:
            os.environ['H1ST_MODEL_REPO_PATH'] = path
            r2_score1 = test_kswe(kswe, data)['r2_score']
            kswe.persist('my_v1')
            kswe = None
            kswe = KSWE()
            kswe.load_params('my_v1')
            r2_score2 = test_kswe(kswe, data)['r2_score']
            assert r2_score1 == r2_score2

    def test_custom_segmentor_and_ensemble(self):
        pass
