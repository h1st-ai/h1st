from h1st.model.ml_model import MLModel
from h1st.model.ml_modeler import MLModeler
from sklearn.preprocessing import RobustScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
import pandas as pd

1. unlabeled_data -> k-model.predict -> k_label (= k-model prediction)
2. unlabeled_data + k_label -> ml-modeler-gen.preprocessor -> preprocessed_data_gen
3. preprocessed_data_gen -> ml-modeler-gen.train -> generalizer
4. unlabeled_data -> gen.predict -> gen_label (= generalizer prediction)
5. unlabeled_data + k_label + gen_label -> ml-modeler-oracle.preprocess -> preprocessed_data_ora
6. preprocessed_data_ora -> ml-modeler-oracle.train -> oracle


class MyGeneralizer(MLModel):
    pass


class MyGenModeler(MLModeler):
    def __init__(self):
        self.stats = {}

    def preprocess(self, data):
        self.stats['scaler'] = RobustScaler(quantile_range=(5.0, 95.0), with_centering=False)
        return self.stats['scaler'].fit_transform(data) 
    
    def train(self, data: Dict[str, Any]) -> Any:
        df = data['df']
        X, y = df[self.stats['sensor_list']], df['y_pred_bool']
        model = LogisticRegression(random_state=0)
        model.fit(X, y)
        return model

#     def evaluate(self, data: Dict, model: MLModel) -> Dict:
#         super().evaluate(data, model)
#         X, y_true = data['test_x'], data['test_y']
#         y_pred = pd.Series(model.predict({'X': X, 'y': y_true})['species']).map(model.stats['targets_dict'])
#         return {'r2_score': r2_score(y_true, y_pred)}    
    
    def build(self, df_labeled_by_k_model: pd.DataFrame):
        df_labeled_by_k_model.loc[self.stats['sensor_list']] = self.preprocess(
            df_labeled_by_k_model[self.stats['sensor_list']])
        base_model = self.train({'df': df_labeled_by_k_model})
        ml_model = self.model_class()
        ml_model.base_model = base_model

        # Pass stats to the model
        if self.stats:
            ml_model.stats = self.stats.copy()
        # Compute metrics and pass to the model
        # ml_model.metrics = self.evaluate(data, ml_model)
        return ml_model

            
class MyEnsemble(MLModel):
    def predict(self, data):
        pass
            
class MyEnsembleModeler(MLModeler):
    def __init__(self):
        self.stats = {}

    def preprocess(self):
        self.stats['scaler'] = RobustScaler(quantile_range=(5.0, 95.0), with_centering=False)
        return self.stats['scaler'].fit_transform(data)         
            
    def train(self, data: Dict[str, Any]) -> Any:
        df = data['df']
        X, y = df[self.stats['sensor_list']], df['y_pred_bool']
        model = RandomForestClassifier(n_jobs=-1, max_depth=4, random_state=42)
        model.fit(X, y)
        return model       
            
    def build(self, df_labeled_by_k_and_gen: pd.DataFrame):
        df_labeled_by_k_and_gen.loc[self.stats['sensor_list']] = self.preprocess(
            df_labeled_by_k_and_gen[self.stats['sensor_list']])
        base_model = self.train({'df': df_labeled_by_k_and_gen})
        ml_model = self.model_class()
        ml_model.base_model = base_model

        # Pass stats to the model
        if self.stats:
            ml_model.stats = self.stats.copy()
        # Compute metrics and pass to the model
        ml_model.metrics = self.evaluate(data, ml_model)        

feature_list = ['feature_1', 'feature_2']
            
my_boolean_model = MyBooleanModel()
df_data = pd.read_parquet(path_to_unlabled_data)
df_data.loc['y_pred_bool'] = my_boolean_model.predict({
    'X': df_data[feature_list]
})

my_gen_modeler = MyGenModeler()
my_gen_modeler.model_class = MyGeneralizer
my_gen_modeler.stats['sensor_list'] = sensor_list
my_gen = my_gen_modeler.build(df_data)
df_data.loc['y_pred_gen'] = my_gen.predict({'X': df_data[feature_list]})

my_ensemble_modeler = MyEnsembleModeler()
my_ensemble_modeler.model_class = MyEnsemble
my_ensemble_modeler.stats['sensor_list'] = sensor_list + ['y_pred_bool', 'y_pred_gen']            
my_ensemble = my_ensemble_modeler.build(df_data)            
df_data.loc['y_pred_ens'] = my_ensemble.predict({'X': df_data[feature_list]})
            

            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            

