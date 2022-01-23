import os
import tempfile
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
        
        return {'pred': pred}

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

        training_data = oracle.generate_data(data['training_data'], id_col='machineID', ts_col='date')

        pred = oracle.predict(data['training_data'])['pred']
        assert len(pred) == len(training_data['y'])