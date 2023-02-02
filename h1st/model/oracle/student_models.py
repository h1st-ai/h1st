from typing import Any, Dict
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from pandas import DataFrame
from h1st.model.ml_model import MLModel


class RandomForestModel(MLModel):
    name = 'RandomForestModel'
    '''
    Knowledge Generalization Model backed by a RandomForest algorithm
    '''

    def predict(self, input_data: dict) -> dict:
        '''
        Implement logic to generate prediction from data
        :params input_data: an dictionary with key `X` containing the data to get predictions.
        :returns: a dictionary with key `predictions` containing the predictions
        '''
        if self.stats['scaler'] is not None:
            x = self.stats['scaler'].transform(input_data['X'])
        else:
            x = input_data['X']

        predict_df = DataFrame(
            self.base_model.predict(x), columns=self.stats['output_labels']
        )
        return {'predictions': predict_df}

    def predict_proba(self, input_data: dict) -> dict:
        if self.stats['scaler'] is not None:
            x = self.stats['scaler'].transform(input_data['X'])
        else:
            x = input_data['X']
        return {'predictions': self.base_model.predict_proba(x)}
    
    def _preprocess(self, data):
        self.stats["scaler"] = StandardScaler()
        return self.stats["scaler"].fit_transform(data)

    def train(self, prepared_data: Dict[str, Any]) -> Any:
        X = self._preprocess(prepared_data['X_train'])
        y = prepared_data['y_train']
        model = RandomForestClassifier(max_depth=20, random_state=1)
        model.fit(X, y)
        self.stats['input_features'] = list(prepared_data['X_train'].columns)
        self.stats['output_labels'] = list(prepared_data['y_train'].columns)


        if self.stats is not None:
            model.stats = self.stats.copy()
        # Compute metrics and pass to the model
        # model.metrics = self.evaluate_model(data, model)
        return model



class LogisticRegressionModel(MLModel):
    name = 'LogisticRegressionModel'
    '''
    Knowledge Generalization Model backed by a Logistic Regression algorithm
    '''

    def predict(self, input_data: dict) -> dict:
        '''
        Implement logic to generate prediction from data
        :params input_data: an dictionary with key `X` containing the data to get predictions.
        :returns: a dictionary with key `predictions` containing the predictions
        '''
        if self.stats['scaler'] is not None:
            x = self.stats['scaler'].transform(input_data['X'])
        else:
            x = input_data['X']

        predict_df = DataFrame(
            self.base_model.predict(x), columns=self.stats['output_labels']
        )
        return {'predictions': predict_df}

    def predict_proba(self, input_data: dict) -> dict:
        if self.stats['scaler'] is not None:
            x = self.stats['scaler'].transform(input_data['X'])
        else:
            x = input_data['X']
        return {'predictions': self.base_model.predict_proba(x)}
