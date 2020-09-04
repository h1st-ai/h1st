import h1st as h1
import sklearn
from sklearn.linear_model import LogisticRegression
import joblib
from unittest import TestCase, skip
import numpy as np
import pandas as pd
from h1st.core.ensemble import MultiOutputClassifierEnsemble

def get_numpy_data(nums_input):
    a = [[1, 1, 1, 1, 1, 1, 1]]
    b = [a * nums_input]
    numpy_data = np.array(b)
    numpy_data = numpy_data.reshape((-1, len(a[0])))
    return numpy_data

class ModelA(h1.Model):
    def __init__(self):
        pass
    def predict(self, input_data):
        nums_input = len(input_data['results'])
        numpy_data = get_numpy_data(nums_input)
        sensors = ['CarSpeed', 'SteeringAngle', 'YawRate', 'Gx', 'Gy']
        cols = ['Timestamp','prediction'] + ['prediction_%s' % s for s in sensors]
        df = pd.DataFrame(data=numpy_data, columns=cols)
        return {'result': df}

class MyEnsemble(MultiOutputClassifierEnsemble):
    def __init__(self):
        super().__init__([ModelA(), ModelA()])
        #prediction columns are across individual models 
        sensors = ['CarSpeed', 'SteeringAngle', 'YawRate', 'Gx', 'Gy']
        self.prediction_columns = ['prediction'] + ['prediction_%s' % s for s in sensors]
        self.labels = ['label_1', 'label_2', 'label_3', 'label_4', 'label_5', 'label_6']
        self.car_model = '13Prius'
        self.attack_mode = 'injection'

    def get_data(self):
        train_files = ["tests/core/dummy_test_attack.csv"]
        test_files = ["tests/core/dummy_test_attack.csv"]
        return {'train_data_files': train_files, 'test_data_files': test_files}

    def prep(self, data):
        train_data_files = data['train_data_files']
        train_inputs = []
        train_labels = []

        for filename in train_data_files:
            df = pd.read_csv(filename)
            df_ts = pd.read_csv(filename)
            for c in self.labels:
                df[c] = 1
                df_ts[c] = 1
            train_inputs.append({
                'results': df_ts,
                'filename': filename
            })
            train_labels.append(df[self.labels])

        return {
            'train_data': train_inputs, 
            'train_labels': train_labels,  
        }

class TestEnsembleTestCase(TestCase):
    def test_train_predict(self):
        ensemble = MyEnsemble()
        data = ensemble.get_data()
        prepared_data = ensemble.prep(data)
        ensemble.train(prepared_data)


        numpy_data = get_numpy_data(100)
        sensors = ['CarSpeed', 'SteeringAngle', 'YawRate', 'Gx', 'Gy']
        cols = ['Timestamp','prediction'] + ['prediction_%s' % s for s in sensors]
        df = pd.DataFrame(data=numpy_data, columns=cols)

        res = ensemble.predict({'results': df})['results']
        #assertion predict = number of rows
        assert len(res) == len(df)
