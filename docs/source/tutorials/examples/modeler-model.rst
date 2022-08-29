Modeler and Model with Iris dataset
===================================

This tutorial shows how you can create Modeler and Model using the iris dataset as an example. Firstly, let's create an MLModeler with load_data to load the iris dataset and generate training data to train a LogisticRegression base model in train. The h1st framework provides the build method which calls load_data and train and produces the corresponding MLModel which you needs to define.

.. code-block:: python

    import os
    from typing import Any, Dict
    import tempfile
    import pandas as pd
    from sklearn import datasets
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import f1_score
    from h1st.model.model import Model
    from h1st.model.ml_modeler import MLModeler
    from h1st.model.ml_model import MLModel

    class MyMLModeler(MLModeler):
    def __init__(self):
        self.stats = {}
        self.example_test_data_ratio = 0.2

    def load_data(self) -> Dict:
        df_raw = datasets.load_iris(as_frame=True).frame
        return self.generate_training_data({'df_raw': df_raw})
    
    def preprocess(self, data):
        self.stats['scaler'] = StandardScaler()
        return self.stats['scaler'].fit_transform(data) 
    
    def generate_training_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        df_raw = data['df_raw']
        df_raw.columns = ['sepal_length','sepal_width','petal_length','petal_width', 'species']
        
        self.stats['targets'] = ['Setosa', 'Versicolour', 'Virginica']
        self.stats['targets_dict'] = {k: v for v, k in enumerate(self.stats['targets'])}

        # Shuffle all the df_raw
        df_raw = df_raw.sample(frac=1, random_state=5).reset_index(drop=True)
        
        # Preprocess data
        df_raw.loc[:, 'sepal_length':'petal_width'] = self.preprocess(
            df_raw.loc[:, 'sepal_length':'petal_width'])

        # Split to training and testing data
        n = df_raw.shape[0]
        n_test = int(n * self.example_test_data_ratio)
        training_data = df_raw.iloc[n_test:, :].reset_index(drop=True)
        test_data = df_raw.iloc[:n_test, :].reset_index(drop=True)

        # Split the data to features and labels
        train_data_x = training_data.loc[:, 'sepal_length':'petal_width']
        train_data_y = training_data['species']
        test_data_x = test_data.loc[:, 'sepal_length':'petal_width']
        test_data_y = test_data['species']

        # When returning many variables, it is a good practice to give them names:
        return {
            'train_x':train_data_x,
            'train_y':train_data_y,
            'test_x':test_data_x,
            'test_y':test_data_y,
        }

    def train_base_model(self, data: Dict[str, Any]) -> Any:
        X, y = data['train_x'], data['train_y']
        model = LogisticRegression(random_state=0)
        model.fit(X, y)
        return model
    
    def evaluate_model(self, data: Dict, model: MLModel) -> Dict:
        super().evaluate_model(data, model)
        X, y_true = data['test_x'], data['test_y']
        y_pred = pd.Series(model.predict({'x': X, 'y': y_true})['species']).map(model.stats['targets_dict'])
        return {'micro_f1_score': f1_score(y_true, y_pred, average='micro')


Here, we define a MLModel with predict method which will be used to generate prediction.

.. code-block:: python

    class MyMLModel(MLModel):
        def preprocess(self, data: Dict[str, Any]) -> Dict[str, Any]:
            raw_data = data['x']
            return {
                'x': self.stats['scaler'].transform(raw_data)
            }

        def predict(self, input_data: dict) -> dict:
            preprocess_data = self.preprocess(input_data)
            y = self.base_model.predict(preprocess_data['x'])
            return {'species': [self.stats['targets'][item] for item in y]}


Now is the time to use our MLModeler and MLModel to create a classification model and generate prediction.

.. code-block:: python

    my_ml_modeler = MyMLModeler()
    my_ml_modeler.model_class = MyMLModel

    my_ml_model = my_ml_modeler.build_model()

    print(my_ml_model.metrics)

    prediction = my_ml_model.predict({
        'x': pd.DataFrame(
            [[5.1, 3.5, 1.5, 0.2],
            [7.1, 3.5, 1.5, 0.6]], 
            columns=['sepal_length','sepal_width','petal_length','petal_width'])
    })
    prediction


The results:

.. code-block::

    {'micro_f1_score': 0.3}
    {'species': ['Setosa', 'Versicolour']}