import numpy as np
from h1st.model.ml_model import MLModel

class CNNClassifierModel(MLModel):

    name = 'CNN Classifier Model'

    # was predict_window
    def predict(self, input_data: dict) -> dict:
        """
        Implement logic to generate prediction from data
        :params data: data for prediction
        :returns: prediction result as a dictionary
        """
        X = self.prep(input_data[self.data_key])
        output_col = self.stats.get('result_key', 'prediction')
        prediction = self.base_model.predict(X)
        result = pd.DataFrame(
            prediction,
            index=input_data[self.data_key].index,
            columns=[output_col]
        )
        return {self.output_key: result}

    def prep(self, X) -> np.array:
        """
        normalize and wrap data into 4D matrix for CNN training
        """
        norm_vector = self.stats['norm_vector']
        input_columns = self.stats['input_columns']

        # prune and order columns
        X = X[input_columns]
        X = X.to_numpy()

        # Normalize
        X_tmp_norm = X / norm_vector

        # Reshape into 2D per sample. So shape is [N_sample, N_feature, N_time]
        # or [N_sample, N_time, N_feature]
        N_sample = X.shape[0]
        N_features = X.shape[1]
        N_wrap = self.stats['n_wrap']
        N_row = int(N_features / N_wrap)
        if N_features / N_wrap != N_row:
            raise ValueError(f'Odd number of columns in input. '
                             f'Cannot wrap row into 2D matrix'
                             f'Found {N_features} columns, Expected '
                             f'{N_row*N_wrap} based on wrap value of {N_wrap}')

        X_norm = X_tmp_norm.reshape([-1, N_row, N_wrap])

        # Expand to 4D for CNN
        X_out = np.expand_dims(X_norm, axis=3)
        return X_out
