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
        return {'predictions': self.base_model.predict(x)}

    def predict_proba(self, input_data: dict) -> dict:
        if self.stats['scaler'] is not None:
            x = self.stats['scaler'].transform(input_data['X'])
        else:
            x = input_data['X']
        return {'predictions': self.base_model.predict_proba(x)}


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
        return {'predictions': self.base_model.predict(x)}

    def predict_proba(self, input_data: dict) -> dict:
        if self.stats['scaler'] is not None:
            x = self.stats['scaler'].transform(input_data['X'])
        else:
            x = input_data['X']
        return {'predictions': self.base_model.predict_proba(x)}
