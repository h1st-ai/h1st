from h1st.model.xgboost.xgbclassifier import XGBClassifierModel
from h1st.model.xgboost.modeler import XGBRegressionModeler

class XGBClassifierModeler(XGBRegressionModeler):
    model_class = XGBClassifierModel

    def __init__(self, threshold=0.5, **kwargs):
        super().__init__(**kwargs)
        self.stats['threshold'] = float(threshold)
