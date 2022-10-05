import os
import tempfile
from typing import Any, Dict
from h1st.model.oracle.oracle_model import OracleModel
import pandas as pd
from sklearn import datasets, metrics
from sklearn.linear_model import LogisticRegression
from h1st.model.predictive_model import PredictiveModel
from h1st.model.ml_model import MLModel
from h1st.model.ml_modeler import MLModeler
from h1st.model.oracle.oracle import Oracle
from h1st.model.oracle.oracle_modeler import OracleModeler
from h1st.model.oracle.student import AdaBoostModel, AdaBoostModeler, RandomForestModel, RandomForestModeler
from h1st.model.rule_based_model import RuleBasedClassificationModel
from h1st.model.rule_based_modeler import RuleBasedModeler

class RuleModel(PredictiveModel):
    sepal_length_max: float = 6.0
    sepal_length_min: float = 4.0
    sepal_width_min: float = 3.0
    sepal_width_max: float = 4.6
    
    def predict(self, data):
        df = data['X']
        return {'predictions': pd.Series(map(self.predict_setosa, df['sepal_length'], df['sepal_width']), 
                         name='predictions').values}

    def predict_setosa(self, sepal_length, sepal_width):
        return 0 if (self.sepal_length_min <= sepal_length <= self.sepal_length_max) \
                  & (self.sepal_width_min <= sepal_width <= self.sepal_width_max) \
               else 1

class MyMLModel(MLModel):
    def predict(self, input_data: Dict) -> Dict:
        y = self.base_model.predict(input_data['X'])
        return {'predictions': y}

class MyMLModeler(MLModeler):
    def __init__(self, model_class=MyMLModel):
        self.model_class = model_class
        self.stats = {}
    
    def evaluate_model(self, data: Dict, model: MLModel) -> Dict:
        super().evaluate_model(data, model)
        X, y_true = data['X_test'], data['y_test']
        y_pred = pd.Series(model.predict({'X': X, 'y': y_true})['predictions'])
        return {'r2_score': metrics.r2_score(y_true, y_pred)}

    def train_base_model(self, data: Dict[str, Any]) -> Any:
        X, y = data['X_train'], data['y_train']
        model = LogisticRegression(random_state=0)
        model.fit(X, y)
        return model

class TestOracle:
    def load_data(self):
        df_raw = datasets.load_iris(as_frame=True).frame
        df_raw.columns = ['sepal_length','sepal_width','petal_length','petal_width', 'species']
        df_raw['species'] = df_raw['species'].apply(lambda x: 1 if x==0 else 0)

        # randomly split training and testing dataset
        example_test_data_ratio = 0.4
        df_raw = df_raw.sample(frac=1, random_state=7).reset_index(drop=True)
        n = df_raw.shape[0]
        n_test = int(n * example_test_data_ratio)
        training_data = df_raw.iloc[n_test:, :].reset_index(drop=True)
        test_data = df_raw.iloc[:n_test, :].reset_index(drop=True)


        return {'training_data': {'X': training_data[['sepal_length', 'sepal_width']],
                                  'y': training_data['species']
                                 },
                'test_data': {'X': test_data[['sepal_length', 'sepal_width']],
                'y': test_data['species']},
                }

    def test_rule_based_ensemble(self):
        data = self.load_data()
        
        modeler = OracleModeler()
        model = modeler.build_model(
            teacher=RuleModel,
            students=[RandomForestModeler, AdaBoostModeler],
            ensembler=RuleBasedModeler(RuleBasedClassificationModel),
            data={'unlabeled_data': data['training_data']['X']}
        )

        assert type(model) == OracleModel

        prediction = model.predict(data['test_data'])['predictions']
        assert len(prediction) == len(data['test_data']['y'])

        with tempfile.TemporaryDirectory() as path:
            os.environ['H1ST_MODEL_REPO_PATH'] = path
            version = model.persist()

            loaded_model = OracleModel().loads(version)

            assert 'sklearn' in str(type(loaded_model.students[0].base_model))
            new_prediction = loaded_model.predict(data['test_data'])['predictions']
            pred_df = pd.DataFrame({'old': prediction, 'new': new_prediction})
            assert len(pred_df[pred_df['old'] != pred_df['new']]) == 0

    def test_rule_based_ensemble_one_student(self):
        data = self.load_data()
        oracle_modeler = OracleModeler(teacher=RuleModel(),
                                       student_modelers = [RandomForestModeler()],
                                       ensembler_modeler=RuleBasedModeler(model_class=RuleBasedClassificationModel))
        oracle = oracle_modeler.build_model({'unlabeled_data': data['training_data']['X']})

        pred = oracle.predict(data['test_data'])['predictions']
        assert len(pred) == len(data['test_data']['y'])
        assert any(pred != data['test_data']['y'])
        # print(metrics.f1_score(data['test_data']['y'], pred, average='macro'))

        with tempfile.TemporaryDirectory() as path:
            os.environ['H1ST_MODEL_REPO_PATH'] = path
            version = oracle.persist()

            oracle_2 = Oracle().load_params(version)
            
            assert 'sklearn' in str(type(oracle_2.students[0].base_model))
            pred_2 = oracle_2.predict(data['test_data'])['predictions']
            pred_df = pd.DataFrame({'pred': pred, 'pred_2': pred_2})
            assert len(pred_df[pred_df['pred'] != pred_df['pred_2']]) == 0

    def test_ml_ensemble(self):
        data = self.load_data()
        oracle_modeler = OracleModeler(teacher=RuleModel(),
                                       student_modelers = [RandomForestModeler(), AdaBoostModeler()],
                                       ensembler_modeler=MyMLModeler())
        oracle = oracle_modeler.build_model({'unlabeled_data': data['training_data']['X'],
                                             'labeled_data': {'X_train': data['training_data']['X'],
                                                               'y_train': data['training_data']['y'],
                                                               'X_test': data['test_data']['X'],
                                                               'y_test': data['test_data']['y'],
                                                               }
                                            })

        pred = oracle.predict(data['test_data'])['predictions']
        assert len(pred) == len(data['test_data']['y'])
        # print(metrics.f1_score(data['test_data']['y'], pred, average='macro'))

        with tempfile.TemporaryDirectory() as path:
            os.environ['H1ST_MODEL_REPO_PATH'] = path
            version = oracle.persist()

            oracle_2 = Oracle().load_params(version)
            
            assert 'sklearn' in str(type(oracle_2.students[0].base_model))
            pred_2 = oracle_2.predict(data['test_data'])['predictions']
            pred_df = pd.DataFrame({'pred': pred, 'pred_2': pred_2})
            assert len(pred_df[pred_df['pred'] != pred_df['pred_2']]) == 0
