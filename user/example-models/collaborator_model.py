import pandas as pd
from h1st.model.k1st.collaborator_modeler import kCollaboratorModeler
from h1st.model.predictive_model import PredictiveModel
from h1st.model.ml_modeler import MLModeler
from h1st.model.ml_model import MLModel
from sklearn.datasets import load_wine
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from h1st.model.wrapper.multi_model import MultiModel

def prep_wine_data():
    data = load_wine()
    X, Y = load_wine(return_X_y=True, as_frame=True)
    Y = pd.get_dummies(Y)
    Y.columns = ['class_0', 'class_1', 'class_2']
    return X, Y


def prep_modeling_data(X, Y, test_pct=0.2):
    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=test_pct)
    return {
        'x_train': X_train,
        'y_train': Y_train,
        'x_test': X_test,
        'y_test': Y_test
    }


class WineKnowledgeModel(PredictiveModel):

    name = 'WineKnowledgeModel'
    data_key = 'x'
    output_key = 'predictions'
    wine_class = None

    def __init__(self):
        super().__init__()
        self.stats = {}
        self.metrics = {}

    def predict(self, input_data: dict):
        X = input_data[self.data_key]
        out = X.apply(self.process_row, axis=1)
        out = pd.Series(out, name=self.wine_class)
        return {self.output_key: out}

    def process_row(self, row):
        return None


class Class0Model(WineKnowledgeModel):

    name = 'WineKnowledgeModel-Class_0'
    wine_class = 'class_0'

    def process_row(self, row):
        if row['proline'] > 985:
            return 1
        
        return 0

class Class1Model(WineKnowledgeModel):

    name = 'WineKnowledgeModel-Class_1'
    wine_class = 'class_1'

    def process_row(self, row):
        if row['ash'] < 3:
            return 1
        return 0

class Class2Model(WineKnowledgeModel):

    name = 'WineKnowledgeModel-Class_2'
    wine_class = 'class_2'

    def process_row(self, row):
        if row['magnesium'] < 120:
            return 1
        return 0

class LogisticRegressionModel(MLModel):

    name = 'LogisticRegressionModel'
    data_key = 'x'
    output_key = 'predictions'

    def __init__(self):
        super().__init__()
        self.stats = {}

    def predict(self, input_data: dict):
        X = input_data[self.data_key]
        pred = pd.Series(self.base_model.predict(X), index=X.index)
        return {self.output_key: pred}

class LogisticRegressionModeler(MLModeler):

    model_class = LogisticRegressionModel

    def __init__(self, result_key=None):
        super().__init__()
        self.stats = {}
        self.result_key = result_key

    def train_base_model(self, prepared_data):
        X = prepared_data['x_train']
        Y = prepared_data['y_train']
        if self.result_key is not None:
            Y = Y[self.result_key]
        elif isinstance(Y, pd.DataFrame) and Y.shape[1] > 1:
            raise ValueError('Y must be a Series or target Y column must be specified')

        base_model = LogisticRegression(random_state=42).fit(X,Y)
        return base_model


if __name__=="__main__":
    X, Y = prep_wine_data()
    prepared_data = prep_modeling_data(X, Y)

    wine_classes = ['class_0', 'class_1', 'class_2']
    wine_kmodels = {
        'class_0': Class0Model(),
        'class_1': Class1Model(),
        'class_2': Class2Model()
    }
    wine_ml_modelers = {x: LogisticRegressionModeler(x) for x in wine_classes}

    wine_model = MultiModel()
    for x in wine_classes:
        modeler = kCollaboratorModeler()
        model = modeler.build_model(
            prepared_data,
            modelers = [wine_ml_modelers[x]],
            models = [wine_kmodels[x]]
        )
        wine_model.add_model(model, name=x)

    version = wine_model.persist()
    print(f'{wine_model.__class__.__name__} model persisted '
          f'with version {version}')

    x_test = prepared_data['x_test']
    #y_pred = wine_model.predict(
    #    {wine_model.data_key: x_test}
    #)[wine_model.output_key]
    #print('Test Predictions')
    #print(y_pred)

    loaded_model = MultiModel().load(version)
    print(f'Successfully loaded model version {version}')
    y_pred = loaded_model.predict(
        {wine_model.data_key: x_test}
    )[wine_model.output_key]
    print('Test Predictions')
    print(y_pred)

