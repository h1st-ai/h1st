import numpy as np
import pandas as pd
from sklearn.multioutput import MultiOutputClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression, LogisticRegressionCV

from h1st.core.model import Model


class StackEnsemble(Model):
    def __init__(self, models, ensembler):
        self.models = models
        # must have .fit() / .predict(), currently assumes sklearn
        self.model = ensembler

    def _extract_prediction(self, results):
        if not isinstance(results, dict):
            raise ValueError('output of ensemble submodel must return a dict with only one key')

        key = 'results'
        if len(list(results)) == 1:
            key = list(results)[0]
        else:
            raise ValueError('output of ensemble submodel must return a dict with only one key')

        if not isinstance(results[key], pd.DataFrame):
            raise ValueError('value of dictionary must be pandas.dataframe')

        return results[key]

    def predict(self, input_data):
        """
        Predicts output for input_data.
        The predicted class or predicted value of an input sample is estmiated prediction based on individual models prediction. 
        
        :param input_data: dictionary with values is a dataframe of numpy array. 
        :returns: dictionary of predicted value/class. The key must be results and values is Pandas Dataframe or numpy array
        """

        df_results = None
        inputs = None
        for i, model in enumerate(self.models):
            df_prediction = self._extract_prediction(model.predict(input_data))
            df_prediction = df_prediction[self.prediction_columns]

            
            df_prediction.fillna(0, inplace=True)
            remain_columns = list(set(df_prediction.columns) - set(self.prediction_columns))
            df_results = df_prediction[remain_columns]
            if inputs is None:
                inputs = df_prediction.values
            else:
                inputs = np.hstack((inputs, df_prediction.values))
            
        #debug length of input
        # assumption: inptus are numpy array (or pandas)
        ensemble_prediction = self.model.predict(inputs)
        
        df_predictions = pd.DataFrame(ensemble_prediction, columns=self.prediction_columns)
        df_results.reset_index(drop=True, inplace=True)
        df_predictions.reset_index(drop=True, inplace=True)
        df_results = pd.concat([df_results, df_predictions], axis=1)
        assert len(df_results) == len(df_predictions)

        return { 'results': df_results }

    def train(self, prepared_data):
        """
        Trains the StackEnsemble.

        :param prepared_data: Dictionary object contains train data, labels and validation data.
        """
        train_data = prepared_data['train_data']
        train_labels = prepared_data['train_labels']
        all_inputs = None
        all_labels = None
        
        for each_input, each_label in zip(train_data, train_labels):
            inputs = None
            labels = each_label
            for model in self.models:
                df_prediction = self._extract_prediction(model.predict(each_input))
                
                df_prediction = df_prediction[self.prediction_columns]
                df_prediction.fillna(0, inplace=True)
                p1 = df_prediction.values
                if inputs is None:
                    inputs = p1
                else:
                    inputs = np.hstack((inputs, p1))
            if all_inputs is None:
                all_inputs = inputs
            else:
                all_inputs = np.vstack((all_inputs, inputs))
            if all_labels is None:
                all_labels = labels
            else:
                all_labels = np.vstack((all_labels, labels))

        # assumption: all_inputs ~ numpy array, all_labels ~ numpy array
        self.model.fit(all_inputs, all_labels)


class MultiOutputClassifierEnsemble(StackEnsemble):
    def __init__(self, models):
        ensembler = MultiOutputClassifier(RandomForestClassifier(n_jobs=-1, max_depth=4, random_state=42))
        super().__init__(models, ensembler)
