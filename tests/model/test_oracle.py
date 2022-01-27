import os
import tempfile
import pandas as pd
from sklearn import datasets, metrics
from h1st.model.oracle.oracle import Oracle
from h1st.model.oracle.student import RandomForestModeler

class RuleModel:
    sepal_length_max: float = 6.0
    sepal_length_min: float = 4.0
    sepal_width_min: float = 3.0
    sepal_width_max: float = 4.6
    
    def predict(self, data):
        df = data['X']
        return {'predictions': pd.Series(map(self.predict_setosa, df['sepal_length'], df['sepal_width']), 
                         name='prediction')}

    
    def predict_setosa(self, sepal_length, sepal_width):
        return 0 if (self.sepal_length_min <= sepal_length <= self.sepal_length_max) \
                  & (self.sepal_width_min <= sepal_width <= self.sepal_width_max) \
               else 1

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


        return {'training_data': {'X': training_data[['sepal_length', 'sepal_width']]},
                'test_data': {'X': test_data[['sepal_length', 'sepal_width']],
                'y': test_data['species']},
                }

    def test_iris(self):
        data = self.load_data()
        oracle = Oracle(knowledge_model=RuleModel())
        oracle.build(data['training_data'])

        pred = oracle.predict(data['test_data'])['predictions']
        assert len(pred) == len(data['test_data']['y'])
        # print(metrics.f1_score(data['test_data']['y'], pred, average='macro'))

        with tempfile.TemporaryDirectory() as path:
            os.environ['H1ST_MODEL_REPO_PATH'] = path
            version = oracle.persist()

            oracle_2 = Oracle(knowledge_model=RuleModel())
            oracle_2.load_params(version)
            
            assert 'sklearn' in str(type(oracle_2.students[0].base_model))
            pred_2 = oracle_2.predict(data['test_data'])['predictions']
            pred_df = pd.concat((pred, pred_2), axis=1)
            pred_df.columns = ['predictions', 'pred_2']
            assert len(pred_df[pred_df['predictions'] != pred_df['pred_2']]) == 0

    def test_iris_one_student(self):
        data = self.load_data()
        oracle = Oracle(knowledge_model=RuleModel(), student_modelers=[RandomForestModeler()])
        oracle.build(data['training_data'])

        pred = oracle.predict(data['test_data'])['predictions']
        assert len(pred) == len(data['test_data']['y'])
        assert any(pred != data['test_data']['y'])
        # print(metrics.f1_score(data['test_data']['y'], pred, average='macro'))

        with tempfile.TemporaryDirectory() as path:
            os.environ['H1ST_MODEL_REPO_PATH'] = path
            version = oracle.persist()

            oracle_2 = Oracle(knowledge_model=RuleModel(), student_modelers=[RandomForestModeler()])
            oracle_2.load_params(version)
            
            assert 'sklearn' in str(type(oracle_2.students[0].base_model))
            pred_2 = oracle_2.predict(data['test_data'])['predictions']
            pred_df = pd.concat((pred, pred_2), axis=1)
            pred_df.columns = ['predictions', 'pred_2']
            assert len(pred_df[pred_df['predictions'] != pred_df['pred_2']]) == 0