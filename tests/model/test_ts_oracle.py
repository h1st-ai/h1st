# import os
# import tempfile
# from typing import Any, Dict
# import pandas as pd
# import numpy as np
# from sklearn import datasets, metrics
# from sklearn.linear_model import LogisticRegression
# from h1st.model.predictive_model import PredictiveModel
# from h1st.model.ml_model import MLModel
# from h1st.model.ml_modeler import MLModeler
# from h1st.model.oracle.student_modelers import RandomForestModeler
# from h1st.model.oracle.student_models import RandomForestModel
# from h1st.model.oracle.ts_oracle_model import TimeSeriesOracleModel
# from h1st.model.oracle.ts_oracle_modeler import TimeseriesOracleModeler
# from h1st.model.rule_based_model import RuleBasedClassificationModel
# from h1st.model.rule_based_modeler import RuleBasedModeler

# dir_path = os.path.dirname(os.path.realpath(__file__))


# class RuleModel(PredictiveModel):
#     daily_thresholds = {
#         'volt': 180,  # >
#         'rotate': 410,  # <
#         'vibration': 44,  # >
#     }

#     def predict(self, input_data):
#         df = input_data['X']
#         df_resampled = df.mean(axis=0)
#         volt_val = df_resampled['volt']
#         rotate_val = df_resampled['rotate']
#         vibration_val = df_resampled['vibration']

#         pred = 0  # Normal
#         if volt_val > self.daily_thresholds['volt']:
#             pred = 1  # fault 1
#         elif rotate_val < self.daily_thresholds['rotate']:
#             pred = 2  # fault 2
#         elif vibration_val > self.daily_thresholds['vibration']:
#             pred = 3  # fault 3

#         return {'predictions': pred}


# class MyMLModel(MLModel):
#     def predict(self, input_data: Dict) -> Dict:
#         y = self.base_model.predict(input_data['X'])
#         return {'predictions': y}


# class MyMLModeler(MLModeler):
#     def __init__(self, model_class=MyMLModel):
#         self.model_class = model_class
#         self.stats = {}

#     def evaluate_model(self, data: Dict, model: MLModel) -> Dict:
#         super().evaluate_model(data, model)
#         X, y_true = data['X_test'], data['y_test']
#         y_pred = pd.Series(model.predict({'X': X, 'y': y_true})['predictions'])
#         return {'r2_score': metrics.r2_score(y_true, y_pred)}

#     def train_base_model(self, data: Dict[str, Any]) -> Any:
#         X, y = data['X_train'], data['y_train']
#         model = LogisticRegression(random_state=0)
#         model.fit(X, y)
#         return model


# class TestTimeSeriesOracle:
#     def load_data(self):
#         # path = f'{dir_path}/data/'
#         # if not os.path.exists(path):
#         #     path = 'https://azuremlsampleexperiments.blob.core.windows.net/datasets/'
#         # telemetry_url = 'PdM_telemetry.csv'
#         # df = pd.read_csv(path + 'PdM_telemetry.csv')
#         # df.loc[:, 'datetime'] = pd.to_datetime(df['datetime'])
#         # df.loc[:, 'datetime'] = df['datetime'] - pd.Timedelta(hours=6)

#         # df_machines = pd.read_csv(path + 'PdM_machines.csv')
#         # df = df.join(df_machines.set_index('machineID'), on='machineID')

#         # df.loc[:, 'date'] = df['datetime'].dt.date

#         # df.sort_values(['machineID', 'datetime'], inplace=True)
#         datetime = [
#             '2015-01-01 06:00:00',
#             '2015-01-01 07:00:00',
#             '2015-01-01 08:00:00',
#             '2015-01-01 09:00:00',
#             '2015-01-01 10:00:00',
#             '2015-01-01 11:00:00',
#             '2015-01-01 12:00:00',
#             '2015-01-01 13:00:00',
#             '2015-01-01 14:00:00',
#             '2015-01-01 15:00:00',
#             '2015-01-01 16:00:00',
#             '2015-01-01 17:00:00',
#             '2015-01-01 18:00:00',
#             '2015-01-01 19:00:00',
#             '2015-01-01 20:00:00',
#             '2015-01-01 21:00:00',
#             '2015-01-01 22:00:00',
#             '2015-01-01 23:00:00',
#             '2015-01-02 00:00:00',
#             '2015-01-02 01:00:00',
#             '2015-01-02 02:00:00',
#             '2015-01-02 03:00:00',
#             '2015-01-02 04:00:00',
#             '2015-01-02 05:00:00',
#             '2015-01-02 06:00:00',
#             '2015-01-02 07:00:00',
#             '2015-01-02 08:00:00',
#             '2015-01-02 09:00:00',
#             '2015-01-02 10:00:00',
#             '2015-01-02 11:00:00',
#             '2015-01-02 12:00:00',
#             '2015-01-02 13:00:00',
#             '2015-01-02 14:00:00',
#             '2015-01-02 15:00:00',
#             '2015-01-02 16:00:00',
#             '2015-01-02 17:00:00',
#             '2015-01-02 18:00:00',
#             '2015-01-02 19:00:00',
#             '2015-01-02 20:00:00',
#             '2015-01-02 21:00:00',
#             '2015-01-02 22:00:00',
#             '2015-01-02 23:00:00',
#             '2015-01-03 00:00:00',
#             '2015-01-03 01:00:00',
#             '2015-01-03 02:00:00',
#             '2015-01-03 03:00:00',
#             '2015-01-03 04:00:00',
#             '2015-01-03 05:00:00',
#         ]
#         machineID = [
#             1,
#             1,
#             1,
#             1,
#             1,
#             1,
#             1,
#             1,
#             1,
#             1,
#             1,
#             1,
#             1,
#             1,
#             1,
#             1,
#             1,
#             1,
#             1,
#             1,
#             1,
#             1,
#             1,
#             1,
#             1,
#             1,
#             1,
#             1,
#             1,
#             1,
#             1,
#             1,
#             1,
#             1,
#             1,
#             1,
#             1,
#             1,
#             1,
#             1,
#             1,
#             1,
#             1,
#             1,
#             1,
#             1,
#             1,
#             1,
#         ]
#         volt = [
#             176.21785302,
#             162.8792229,
#             170.98990241,
#             162.46283326,
#             157.61002119,
#             172.5048392,
#             156.55603061,
#             172.52278081,
#             175.32452392,
#             169.21842325,
#             167.06098072,
#             160.26395373,
#             153.35349153,
#             182.73911304,
#             170.33543789,
#             182.46710926,
#             151.33568223,
#             172.53539621,
#             180.0974946,
#             169.60585435,
#             167.12911747,
#             158.2714003,
#             200.87242982,
#             181.2575218,
#             197.36312454,
#             171.20089462,
#             160.52886052,
#             147.3006782,
#             160.45850253,
#             173.39452299,
#             185.20535521,
#             173.79125203,
#             152.42077531,
#             180.03071493,
#             145.24848598,
#             164.51221628,
#             165.25822507,
#             140.77630929,
#             183.80086284,
#             160.65692608,
#             164.98945025,
#             190.92721839,
#             179.55011617,
#             168.37352455,
#             177.70644168,
#             175.98907711,
#             194.94284671,
#             174.13840105,
#         ]
#         rotate = [
#             418.50407822,
#             402.74748957,
#             527.34982545,
#             346.14933504,
#             435.37687302,
#             430.32336211,
#             499.07162307,
#             409.624717,
#             398.64878071,
#             460.85066993,
#             382.48354291,
#             448.08425597,
#             490.67292103,
#             418.19925197,
#             402.46118655,
#             501.91897273,
#             444.92265646,
#             511.88636426,
#             486.71230393,
#             519.45281207,
#             427.05076812,
#             422.81105173,
#             403.23595079,
#             495.77795782,
#             446.94394729,
#             384.64596164,
#             486.45905612,
#             420.61079177,
#             412.96569562,
#             439.57945979,
#             445.60644669,
#             385.35492384,
#             497.84062007,
#             486.89359305,
#             495.37644918,
#             424.54263259,
#             493.1614285,
#             432.04377328,
#             414.27429508,
#             446.61384264,
#             418.06979141,
#             437.96044129,
#             502.78745627,
#             489.91089775,
#             521.83793638,
#             510.25697608,
#             418.84227126,
#             489.25031515,
#         ]
#         pressure = [
#             113.07793546,
#             95.46052538,
#             75.23790486,
#             109.24856128,
#             111.88664821,
#             95.92704169,
#             111.75568429,
#             101.00108276,
#             110.62436055,
#             104.84822997,
#             103.78066251,
#             96.48097567,
#             86.01244025,
#             93.48495406,
#             93.23578706,
#             85.7626147,
#             94.24737133,
#             91.32942907,
#             96.73391515,
#             78.88077957,
#             91.69989877,
#             92.43913192,
#             96.53548653,
#             93.43929005,
#             114.34206081,
#             103.37329327,
#             86.94427269,
#             110.40898468,
#             90.7113545,
#             97.67582686,
#             105.99324663,
#             99.50681883,
#             101.64169147,
#             93.7438266,
#             111.95058726,
#             102.48552981,
#             127.01449775,
#             99.82449701,
#             86.32375989,
#             115.31331185,
#             80.66828673,
#             85.26024735,
#             109.9660202,
#             114.04240618,
#             101.5280331,
#             92.36287247,
#             95.89631223,
#             91.92630609,
#         ]
#         vibration = [
#             45.08768576,
#             43.41397268,
#             34.17884712,
#             41.12214409,
#             25.990511,
#             35.65501733,
#             42.7539197,
#             35.48200866,
#             45.48228685,
#             39.90173544,
#             42.67579991,
#             38.54368093,
#             44.10855437,
#             41.36718973,
#             39.73988268,
#             51.02148612,
#             42.11965209,
#             32.24883237,
#             38.89677573,
#             40.15687491,
#             44.6423514,
#             39.78191709,
#             32.51683764,
#             52.35587614,
#             29.52766452,
#             35.79656614,
#             42.99250944,
#             34.20304225,
#             36.96376626,
#             37.11710256,
#             47.86248424,
#             42.92133626,
#             30.66518414,
#             43.09975844,
#             37.42227213,
#             42.24337433,
#             45.13519397,
#             31.27932091,
#             37.78983368,
#             35.944564,
#             42.6386787,
#             40.56620182,
#             41.73069767,
#             36.09265642,
#             35.46844404,
#             36.37603366,
#             47.16364845,
#             32.3236161,
#         ]

#         df = pd.DataFrame(
#             {
#                 'datetime': datetime,
#                 'machineID': machineID,
#                 'volt': volt,
#                 'rotate': rotate,
#                 'pressure': pressure,
#                 'vibration': vibration,
#             }
#         )
#         df.loc[:, 'datetime'] = pd.to_datetime(df['datetime'])
#         df.loc[:, 'datetime'] = df['datetime'] - pd.Timedelta(hours=6)
#         df.sort_values(['machineID', 'datetime'], inplace=True)
#         df.loc[:, 'date'] = df['datetime'].dt.date

#         return {
#             'training_data': {
#                 'X': df.loc[
#                     df.machineID == 1,
#                     ['machineID', 'date', 'volt', 'rotate', 'pressure', 'vibration'],
#                 ]
#             }
#         }

#     def test_rule_based_ensemble(self):
#         data = self.load_data()

#         oracle_modeler = TimeseriesOracleModeler()
#         oracle = oracle_modeler.build_model(
#             data={'unlabeled_data': data['training_data']['X']},
#             teacher=RuleModel(),
#             students=[RandomForestModeler()],
#             ensembler=RuleBasedModeler(RuleBasedClassificationModel),
#             id_col='machineID',
#             ts_col='date',
#         )

#         pred = oracle.predict(data['training_data'])['predictions']
#         assert len(pred) == 2

#         with tempfile.TemporaryDirectory() as path:
#             os.environ['H1ST_MODEL_REPO_PATH'] = path
#             version = oracle.persist()

#             oracle_2 = TimeSeriesOracleModel().load_params(version)

#             assert 'sklearn' in str(type(oracle_2.students[0].base_model))
#             pred_2 = oracle_2.predict(data['training_data'])['predictions']
#             pred_df = pd.DataFrame({'pred': pred, 'pred_2': pred_2})
#             assert len(pred_df[pred_df['pred'] != pred_df['pred_2']]) == 0

#     def test_rule_based_ensemble_with_features(self):
#         data = self.load_data()

#         oracle_modeler = TimeseriesOracleModeler()
#         oracle = oracle_modeler.build_model(
#             data={'unlabeled_data': data['training_data']['X']},
#             teacher=RuleModel(),
#             students=[RandomForestModeler()],
#             ensembler=RuleBasedModeler(RuleBasedClassificationModel),
#             id_col='machineID',
#             ts_col='date',
#             features=['volt', 'rotate', 'vibration'],
#         )

#         pred = oracle.predict(data['training_data'])['predictions']
#         assert len(pred) == 2

#         with tempfile.TemporaryDirectory() as path:
#             os.environ['H1ST_MODEL_REPO_PATH'] = path
#             version = oracle.persist()

#             oracle_2 = TimeSeriesOracleModel().load_params(version)

#             assert 'sklearn' in str(type(oracle_2.students[0].base_model))
#             pred_2 = oracle_2.predict(data['training_data'])['predictions']
#             pred_df = pd.DataFrame({'pred': pred, 'pred_2': pred_2})
#             assert len(pred_df[pred_df['pred'] != pred_df['pred_2']]) == 0

#     def test_rule_based_ensemble_one_equipment(self):
#         data = self.load_data()
#         data['training_data']['X'].drop('machineID', axis=1, inplace=True)

#         oracle_modeler = TimeseriesOracleModeler()
#         oracle = oracle_modeler.build_model(
#             data={'unlabeled_data': data['training_data']['X']},
#             teacher=RuleModel(),
#             students=[RandomForestModeler()],
#             ensembler=RuleBasedModeler(RuleBasedClassificationModel),
#             ts_col='date',
#         )

#         pred = oracle.predict(data['training_data'])['predictions']
#         assert len(pred) == 2

#         with tempfile.TemporaryDirectory() as path:
#             os.environ['H1ST_MODEL_REPO_PATH'] = path
#             version = oracle.persist()

#             oracle_2 = TimeSeriesOracleModel().load_params(version)

#             assert 'sklearn' in str(type(oracle_2.students[0].base_model))
#             pred_2 = oracle_2.predict(data['training_data'])['predictions']
#             pred_df = pd.DataFrame({'pred': pred, 'pred_2': pred_2})
#             assert len(pred_df[pred_df['pred'] != pred_df['pred_2']]) == 0

#     def test_ml_based_ensemble(self):
#         data = self.load_data()
#         num_samples = 2

#         oracle_modeler = TimeseriesOracleModeler()
#         oracle = oracle_modeler.build_model(
#             data={
#                 'unlabeled_data': data['training_data']['X'],
#                 'labeled_data': {
#                     'X_train': data['training_data']['X'],
#                     'y_train': np.array(range(num_samples)),
#                     'X_test': data['training_data']['X'],
#                     'y_test': np.array(range(num_samples)),
#                 },
#             },
#             teacher=RuleModel(),
#             students=[RandomForestModeler()],
#             ensembler=RuleBasedModeler(RuleBasedClassificationModel),
#             id_col='machineID',
#             ts_col='date',
#         )

#         pred = oracle.predict(data['training_data'])['predictions']
#         assert len(pred) == num_samples

#         with tempfile.TemporaryDirectory() as path:
#             os.environ['H1ST_MODEL_REPO_PATH'] = path
#             version = oracle.persist()

#             oracle_2 = TimeSeriesOracleModel().load_params(version)

#             assert 'sklearn' in str(type(oracle_2.students[0].base_model))
#             pred_2 = oracle_2.predict(data['training_data'])['predictions']
#             pred_df = pd.DataFrame({'pred': pred, 'pred_2': pred_2})
#             assert len(pred_df[pred_df['pred'] != pred_df['pred_2']]) == 0
