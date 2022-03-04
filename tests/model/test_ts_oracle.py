import os
import tempfile
from typing import Any, Dict
import pandas as pd
import numpy as np
from sklearn import datasets, metrics
from sklearn.linear_model import LogisticRegression
from h1st.model.ml_model import MLModel
from h1st.model.ml_modeler import MLModeler
from h1st.model.oracle.student import AdaBoostModel, AdaBoostModeler, RandomForestModel, RandomForestModeler
from h1st.model.oracle.ts_oracle import TimeSeriesOracle
from h1st.model.oracle.ts_oracle_modeler import TimeseriesOracleModeler
from h1st.model.rule_based_model import RuleBasedClassificationModel
from h1st.model.rule_based_modeler import RuleBasedModeler

dir_path = os.path.dirname(os.path.realpath(__file__))

class RuleModel:
    daily_thresholds = {
        'volt': 180, # >
        'rotate': 410, # <
        'vibration': 44, # >   
    }

    def predict(self, input_data):
        df = input_data['X']
        df_resampled = df.mean(axis=0)
        volt_val = df_resampled['volt']
        rotate_val = df_resampled['rotate']
        vibration_val = df_resampled['vibration']
        
        pred = 0 # Normal
        if volt_val > self.daily_thresholds['volt']:
            pred = 1 # fault 1
        elif rotate_val < self.daily_thresholds['rotate']:
            pred = 2 # fault 2
        elif vibration_val > self.daily_thresholds['vibration']:
            pred = 3 # fault 3
        
        return {'predictions': pred}

class MyMLModel(MLModel):
    def process(self, input_data: Dict) -> Dict:
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

class TestTimeSeriesOracle:
    def load_data(self):
        path = f'{dir_path}/data/'
        if not os.path.exists(path):
            path = 'https://azuremlsampleexperiments.blob.core.windows.net/datasets/'
        telemetry_url = 'PdM_telemetry.csv'
        df = pd.read_csv(path + 'PdM_telemetry.csv')
        df.loc[:, 'datetime'] = pd.to_datetime(df['datetime'])
        df.loc[:, 'datetime'] = df['datetime'] - pd.Timedelta(hours=6)

        df_machines = pd.read_csv(path + 'PdM_machines.csv')
        df = df.join(df_machines.set_index('machineID'), on='machineID')

        df.loc[:, 'date'] = df['datetime'].dt.date

        df.sort_values(['machineID', 'datetime'], inplace=True)

        return {'training_data': {'X': df.loc[df.machineID==1, ['machineID', 'date', 'volt', 'rotate', 'pressure', 'vibration']]}}
        

    def test_rule_based_ensemble(self):
        data = self.load_data()

        oracle_modeler = TimeseriesOracleModeler(teacher=RuleModel(),
                                        student_modelers = [RandomForestModeler(),
                                                            AdaBoostModeler()],
                                        ensembler_modeler=RuleBasedModeler(model_class=RuleBasedClassificationModel))
        oracle = oracle_modeler.build_model({'unlabelled_data': data['training_data']['X']},
                                            id_col='machineID', ts_col='date')

        pred = oracle.predict(data['training_data'])['predictions']
        assert len(pred) == 366

        with tempfile.TemporaryDirectory() as path:
            os.environ['H1ST_MODEL_REPO_PATH'] = path
            version = oracle.persist()

            oracle_2 = TimeSeriesOracle(teacher=RuleModel(),
                                        students= [RandomForestModel(), AdaBoostModel()],
                                        ensembler=RuleBasedClassificationModel())
            oracle_2.load_params(version)
            
            assert 'sklearn' in str(type(oracle_2.students[0].base_model))
            pred_2 = oracle_2.predict(data['training_data'])['predictions']
            pred_df = pd.DataFrame({'pred': pred, 'pred_2': pred_2})
            assert len(pred_df[pred_df['pred'] != pred_df['pred_2']]) == 0

    def test_rule_based_ensemble_with_features(self):
        data = self.load_data()

        oracle_modeler = TimeseriesOracleModeler(teacher=RuleModel(),
                                        student_modelers = [RandomForestModeler(), AdaBoostModeler()],
                                        ensembler_modeler=RuleBasedModeler(model_class=RuleBasedClassificationModel))
        oracle = oracle_modeler.build_model({'unlabelled_data': data['training_data']['X']},
                                      id_col='machineID',
                                      ts_col='date',
                                      features=['volt', 'rotate', 'vibration']
                                      )

        pred = oracle.predict(data['training_data'])['predictions']
        assert len(pred) == 366

        with tempfile.TemporaryDirectory() as path:
            os.environ['H1ST_MODEL_REPO_PATH'] = path
            version = oracle.persist()

            oracle_2 = TimeSeriesOracle(teacher=RuleModel(),
                                        students= [RandomForestModel(), AdaBoostModel()],
                                        ensembler=RuleBasedClassificationModel())
            oracle_2.load_params(version)
            
            assert 'sklearn' in str(type(oracle_2.students[0].base_model))
            pred_2 = oracle_2.predict(data['training_data'])['predictions']
            pred_df = pd.DataFrame({'pred': pred, 'pred_2': pred_2})
            assert len(pred_df[pred_df['pred'] != pred_df['pred_2']]) == 0

    def test_rule_based_ensemble_one_equipment(self):
        data = self.load_data()
        data['training_data']['X'].drop('machineID', axis=1, inplace=True)
        oracle_modeler = TimeseriesOracleModeler(teacher=RuleModel(),
                                        student_modelers = [RandomForestModeler(), AdaBoostModeler()],
                                        ensembler_modeler=RuleBasedModeler(model_class=RuleBasedClassificationModel))
        oracle = oracle_modeler.build_model({'unlabelled_data': data['training_data']['X']},
                                            ts_col='date')

        pred = oracle.predict(data['training_data'])['predictions']
        assert len(pred) == 366

        with tempfile.TemporaryDirectory() as path:
            os.environ['H1ST_MODEL_REPO_PATH'] = path
            version = oracle.persist()

            oracle_2 = TimeSeriesOracle(teacher=RuleModel(),
                                        students= [RandomForestModel(), AdaBoostModel()],
                                        ensembler=RuleBasedClassificationModel())
            oracle_2.load_params(version)
            
            assert 'sklearn' in str(type(oracle_2.students[0].base_model))
            pred_2 = oracle_2.predict(data['training_data'])['predictions']
            pred_df = pd.DataFrame({'pred': pred, 'pred_2': pred_2})
            assert len(pred_df[pred_df['pred'] != pred_df['pred_2']]) == 0

    def test_ml_based_ensemble(self):
        data = self.load_data()

        oracle_modeler = TimeseriesOracleModeler(teacher=RuleModel(),
                                        student_modelers = [RandomForestModeler(),
                                                            AdaBoostModeler()],
                                        ensembler_modeler=MyMLModeler())

        num_samples = 366
        pseudo_y = np.random.randint(4, size=num_samples)
        oracle = oracle_modeler.build_model({'unlabelled_data': data['training_data']['X'],
                                             'labelled_data': {'X_train': data['training_data']['X'],
                                                               'y_train': pseudo_y,
                                                               'X_test': data['training_data']['X'],
                                                               'y_test': pseudo_y
                                             }
                                            },
                                            id_col='machineID', ts_col='date')

        pred = oracle.predict(data['training_data'])['predictions']
        assert len(pred) == num_samples

        with tempfile.TemporaryDirectory() as path:
            os.environ['H1ST_MODEL_REPO_PATH'] = path
            version = oracle.persist()

            oracle_2 = TimeSeriesOracle(teacher=RuleModel(),
                                        students= [RandomForestModel(), AdaBoostModel()],
                                        ensembler=MyMLModel())
            oracle_2.load_params(version)
            
            assert 'sklearn' in str(type(oracle_2.students[0].base_model))
            pred_2 = oracle_2.predict(data['training_data'])['predictions']
            pred_df = pd.DataFrame({'pred': pred, 'pred_2': pred_2})
            assert len(pred_df[pred_df['pred'] != pred_df['pred_2']]) == 0