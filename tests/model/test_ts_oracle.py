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
    ds = 'datetime'

    def predict(self, input_data):
        df = input_data['X']
        pred = []
        i = 0
        for group_name, group_df in df.groupby(['machineID', 'date']):
            if i >= 100:
                break
            group_df.sort_values(by=self.ds)
            df_resampled = group_df.set_index(self.ds).resample('1d').mean()
            volt_val = df_resampled['volt'].iloc[0]
            rotate_val = df_resampled['rotate'].iloc[0]
            vibration_val = df_resampled['vibration'].iloc[0]
            
        
            if volt_val > self.daily_thresholds['volt']:
                pred.append('1') # fault 1
            elif rotate_val < self.daily_thresholds['rotate']:
                pred.append('2') # fault 2
            elif vibration_val > self.daily_thresholds['vibration']:
                pred.append('3') # fault 3
            else:
                pred.append('0') # Normal

            i += 1
        
        return {'pred': pd.Series(pred)}

class TestOracle:
    def load_data(self):
        path = f'{dir_path}/data/'
        telemetry_url = 'PdM_telemetry.csv'
        df = pd.read_csv(path + 'PdM_telemetry.csv')
        df.loc[:, 'datetime'] = pd.to_datetime(df['datetime'])
        df.loc[:, 'datetime'] = df['datetime'] - pd.Timedelta(hours=6)

        df_machines = pd.read_csv(path + 'PdM_machines.csv')
        df = df.join(df_machines.set_index('machineID'), on='machineID')

        df.loc[:, 'date'] = df['datetime'].dt.date

        df.sort_values(['machineID', 'datetime'], inplace=True)

        return {'training_data': {'X': df[['machineID', 'datetime', 'date', 'volt', 'rotate', 'pressure', 'vibration']]}}
        

    def test_azure_iot(self):
        data = self.load_data()
        rule_model = RuleModel()
        rule_model_pred = rule_model.predict(data['training_data'])

        oracle = TimeSeriesOracle(knowledge_model=RuleModel())
        oracle.build(data['training_data'], id_col='machineID', ts_col='date')

        pred = oracle.predict(data['training_data'])['pred']
        assert len(pred) == len(rule_model_pred['pred'])