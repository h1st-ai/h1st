import os
from typing import Any, Dict
import tempfile
import pandas as pd
from sklearn import datasets
from sklearn.ensemble import AdaBoostClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import r2_score
from h1st.model.rule_based_modeler import RuleBasedModeler
from h1st.model.ensemble.classifier_stack_ensemble_modeler import ClassifierStackEnsembleModeler
from h1st.model.ensemble.stack_ensemble import StackEnsemble
from h1st.model.ensemble.stack_ensemble_modeler import StackEnsembleModeler
from h1st.model.ml_modeler import MLModeler
from h1st.model.ml_model import MLModel
from h1st.model.rule_based_model import RuleBasedClassificationModel

class MyMLModel(MLModel):
    def predict(self, input_data: Dict) -> Dict:
        y = self.base_model.predict(input_data['X'])
        return {'predictions': y}

class MyMLModel1(MyMLModel):
    pass

class MyMLModel2(MyMLModel):
    pass

class MyMLModel3(MyMLModel):
    pass

class MyMLModeler(MLModeler):
    def __init__(self, model_class):
        self.model_class = model_class
        self.stats = {}
    
    def evaluate_model(self, data: Dict, model: MLModel) -> Dict:
        super().evaluate_model(data, model)
        X, y_true = data['X_test'], data['y_test']
        y_pred = pd.Series(model.predict({'X': X, 'y': y_true})['predictions'])
        return {'r2_score': r2_score(y_true, y_pred)}

class MyMLModeler1(MyMLModeler):
    def __init__(self, model_class=MyMLModel1):
        super().__init__(model_class)

    def train_base_model(self, data: Dict[str, Any]) -> Any:
        X, y = data['X_train'], data['y_train']
        model = AdaBoostClassifier(random_state=0)
        model.fit(X, y)
        return model

class MyMLModeler2(MyMLModeler):
    def __init__(self, model_class=MyMLModel2):
        super().__init__(model_class)

    def train_base_model(self, data: Dict[str, Any]) -> Any:
        X, y = data['X_train'], data['y_train']
        model = RandomForestClassifier(random_state=0)
        model.fit(X, y)
        return model

class MyMLModel(MLModel):
    def predict(self, input_data: Dict) -> Dict:
        y = self.base_model.predict(input_data['X'])
        return {'predictions': y}

class MyMLModeler3(MyMLModeler):
    def __init__(self, model_class=MyMLModel3):
        super().__init__(model_class)

    def train_base_model(self, data: Dict[str, Any]) -> Any:
        X, y = data['X_train'], data['y_train']
        model = LogisticRegression(random_state=0)
        model.fit(X, y)
        return model

class TestEnsemble:
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


        return {'X_train': training_data[['sepal_length','sepal_width','petal_length','petal_width']],
                'y_train': training_data['species'],
                'X_test': test_data[['sepal_length','sepal_width','petal_length','petal_width']],
                'y_test': test_data['species'],
                }

class TestRuleBasedStackEnsemble(TestEnsemble):
    def test_train_predict(self):
        data = self.load_data()

        my_ml_modeler1 = MyMLModeler1()

        my_ml_model1 = my_ml_modeler1.build_model(data)

        my_ml_modeler2 = MyMLModeler2()

        my_ml_model2 = my_ml_modeler2.build_model(data)

        rule_based_classification_ensemble_modeler = ClassifierStackEnsembleModeler(
                                                ensembler_modeler=RuleBasedModeler(RuleBasedClassificationModel),
                                                sub_models=[my_ml_model1, my_ml_model2]
                                            )
        
        rule_based_classification_ensemble = rule_based_classification_ensemble_modeler.build_model()

        test_data = {
                'X': pd.DataFrame(
                    [[5.1, 3.5, 1.5, 0.2],
                    [7.1, 3.5, 1.5, 0.6]], 
                    columns=['sepal_length','sepal_width','petal_length','petal_width'])
            }
        
        pred = rule_based_classification_ensemble.predict(test_data)['predictions']
        assert len(pred) == 2


class TestMLStackEnsemble(TestEnsemble):
    def test_train_predict(self):
        data = self.load_data()

        my_ml_modeler1 = MyMLModeler1()

        my_ml_model1 = my_ml_modeler1.build_model(data)

        my_ml_modeler2 = MyMLModeler2()

        my_ml_model2 = my_ml_modeler2.build_model(data)

        stack_ensemble_modeler = StackEnsembleModeler(
                                    ensembler_modeler=MyMLModeler3(MyMLModel3),
                                    sub_models=[my_ml_model1, my_ml_model2]
                                )

        stack_ensemble_model = stack_ensemble_modeler.build_model(data)

        test_data = {
                'X': pd.DataFrame(
                    [[5.1, 3.5, 1.5, 0.2],
                    [7.1, 3.5, 1.5, 0.6]], 
                    columns=['sepal_length','sepal_width','petal_length','petal_width'])
            }
        
        pred = stack_ensemble_model.predict(test_data)['predictions']
        assert len(pred) == 2

        classifier_stack_ensemble_modeler = ClassifierStackEnsembleModeler(
                                                ensembler_modeler=MyMLModeler3(),
                                                sub_models=[my_ml_model1, my_ml_model2]
                                            )

        classifier_stack_ensemble_model = classifier_stack_ensemble_modeler.build_model(data)

        pred_2 = classifier_stack_ensemble_model.predict(test_data)['predictions']
        assert len(pred_2) == 2

        with tempfile.TemporaryDirectory() as path:
            os.environ['H1ST_MODEL_REPO_PATH'] = path
            version = stack_ensemble_model.persist()
            stack_ensemble_model_2 = StackEnsemble(
                                    ensembler=MyMLModel3(),
                                    sub_models=[my_ml_model1, my_ml_model2]
                                )

            stack_ensemble_model_2.load_params(version)

            assert 'sklearn' in str(type(stack_ensemble_model_2.ensembler.base_model))
            pred_3 = stack_ensemble_model_2.predict(test_data)['predictions']
            pred_df = pd.concat((pd.Series(pred), pd.Series(pred_3)), axis=1)
            pred_df.columns = ['pred', 'pred_3']
            assert len(pred_df[pred_df['pred'] != pred_df['pred_3']]) == 0
