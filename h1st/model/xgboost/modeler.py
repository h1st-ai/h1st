from xgboost import XGBRegressor

from h1st.model.model import Model
from h1st.model.modeler import Modeler


class XGBoostModeler(Modeler):
    def __init__(self, model_class=None) -> None:
        self.stats = {}
        if model_class is None:
            self.model_class = XGBRegressor
        else:
            self.model_class = model_class
    
    def build_model(self, data: dict = None) -> Model:
        x_train = data.get('X_train')
        y_train = data.get('y_train')
        model = self.model_class()
        
        model.fit(x_train, y_train)
        return model

    def evaluate_model(self, prepared_data: dict, model: Model) -> dict:
        pass
