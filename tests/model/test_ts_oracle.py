import os
from pyexpat import features
import tempfile
from typing import Dict
import pandas as pd
from sklearn import datasets, metrics
from h1st.model.oracle.ts_oracle import TimeSeriesOracle

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
        

    def test_azure_iot(self):
        data = self.load_data()

        oracle = TimeSeriesOracle(knowledge_model=RuleModel())
        oracle.build(data['training_data'], id_col='machineID', ts_col='date')

        training_data = oracle.generate_data(data['training_data'])

        pred = oracle.predict(data['training_data'])['predictions']
        assert len(pred) == len(training_data['y'])

        with tempfile.TemporaryDirectory() as path:
            os.environ['H1ST_MODEL_REPO_PATH'] = path
            version = oracle.persist()

            oracle_2 = TimeSeriesOracle(knowledge_model=RuleModel())
            oracle_2.load_params(version)
            
            assert 'sklearn' in str(type(oracle_2.students[0].base_model))
            pred_2 = oracle_2.predict(data['training_data'])['predictions']
            pred_df = pd.concat((pred, pred_2), axis=1)
            pred_df.columns = ['predictions', 'pred_2']
            assert len(pred_df[pred_df['predictions'] != pred_df['pred_2']]) == 0

    def test_azure_iot_with_features(self):
        data = self.load_data()

        oracle = TimeSeriesOracle(knowledge_model=RuleModel())
        oracle.build(data['training_data'],
                    id_col='machineID',
                    ts_col='date',
                    features=['volt', 'rotate', 'vibration']
                    )

        training_data = oracle.generate_data(data['training_data'])

        pred = oracle.predict(data['training_data'])['predictions']
        assert len(pred) == len(training_data['y'])

        with tempfile.TemporaryDirectory() as path:
            os.environ['H1ST_MODEL_REPO_PATH'] = path
            version = oracle.persist()

            oracle_2 = TimeSeriesOracle(knowledge_model=RuleModel())
            oracle_2.load_params(version)
            
            assert 'sklearn' in str(type(oracle_2.students[0].base_model))
            pred_2 = oracle_2.predict(data['training_data'])['predictions']
            pred_df = pd.concat((pred, pred_2), axis=1)
            pred_df.columns = ['predictions', 'pred_2']
            assert len(pred_df[pred_df['predictions'] != pred_df['pred_2']]) == 0

    def test_azure_iot_one_equipment(self):
        data = self.load_data()
        data['training_data']['X'].drop('machineID', axis=1, inplace=True)
        oracle = TimeSeriesOracle(knowledge_model=RuleModel())
        oracle.build(data['training_data'], ts_col='date')

        training_data = oracle.generate_data(data['training_data'])

        pred = oracle.predict(data['training_data'])['predictions']
        assert len(pred) == len(training_data['y'])

        with tempfile.TemporaryDirectory() as path:
            os.environ['H1ST_MODEL_REPO_PATH'] = path
            version = oracle.persist()

            oracle_2 = TimeSeriesOracle(knowledge_model=RuleModel())
            oracle_2.load_params(version)
            
            assert 'sklearn' in str(type(oracle_2.students[0].base_model))
            pred_2 = oracle_2.predict(data['training_data'])['predictions']
            pred_df = pd.concat((pred, pred_2), axis=1)
            pred_df.columns = ['predictions', 'pred_2']
            assert len(pred_df[pred_df['predictions'] != pred_df['pred_2']]) == 0