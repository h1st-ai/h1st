import tempfile
import os
import pandas as pd
import numpy as np
from sklearn import datasets

from h1st.model.fuzzy import (
    FuzzyVariables,
    FuzzyMembership as fm,
    FuzzyRules,
    FuzzyModeler,
)
from h1st.model.oracle.oracle import Oracle
from h1st.model.oracle.oracle_modeler import OracleModeler
from h1st.model.oracle.ensembler_models import MajorityVotingEnsembleModel
from h1st.model.oracle.ensembler_modelers import MLPEnsembleModeler
from h1st.model.oracle.student_modelers import (
    LogisticRegressionModeler,
    RandomForestModeler,
)
from h1st.model.rule_based_model import RuleBasedModel
from h1st.model.rule_based_modeler import RuleBasedModeler


class RuleModel(RuleBasedModel):
    sepal_length_max: float = 6.0
    sepal_length_min: float = 4.0
    sepal_width_min: float = 2.8
    sepal_width_max: float = 4.6

    def predict(self, data):
        df = data['X']
        return {
            'predictions': pd.DataFrame(
                map(self.predict_setosa, df['sepal_length'], df['sepal_width']),
                columns=['setosa'],
            )
        }

    def predict_setosa(self, sepal_length, sepal_width):
        return (
            1
            if (self.sepal_length_min <= sepal_length <= self.sepal_length_max)
            & (self.sepal_width_min <= sepal_width <= self.sepal_width_max)
            else 0
        )


def build_fuzzy_model(data):
    def get_metadata(data):
        res = {}
        for k, v in data['training_data']['X'].max().to_dict().items():
            res[k] = {'max': v}
        for k, v in data['training_data']['X'].min().to_dict().items():
            res[k].update({'min': v})
        return res

    metadata = get_metadata(data)
    fuzzy_vars = FuzzyVariables()
    fuzzy_vars.add(
        var_name='sepal_length',
        var_type='antecedent',
        var_range=np.arange(
            metadata['sepal_length']['min'], metadata['sepal_length']['max'], 0.1
        ),
        membership_funcs=[
            ('small', fm.GAUSSIAN, [5, 0.7]),
            ('large', fm.TRAPEZOID, [5.8, 6.4, 8, 8]),
        ],
    )
    fuzzy_vars.add(
        var_name='sepal_width',
        var_type='antecedent',
        var_range=np.arange(
            metadata['sepal_width']['min'], metadata['sepal_width']['max'], 0.1
        ),
        membership_funcs=[
            ('small', fm.GAUSSIAN, [2.8, 0.15]),
            ('large', fm.GAUSSIAN, [3.3, 0.25]),
        ],
    )
    fuzzy_vars.add(
        var_name='setosa',
        var_type='consequent',
        var_range=np.arange(0, 1 + 1e-5, 0.1),
        membership_funcs=[
            ('false', fm.GAUSSIAN, [0, 0.4]),
            ('true', fm.GAUSSIAN, [1, 0.4]),
        ],
    )
    fuzzy_vars.add(
        var_name='non_setosa',
        var_type='consequent',
        var_range=np.arange(0, 1 + 1e-5, 0.1),
        membership_funcs=[
            ('false', fm.GAUSSIAN, [0, 0.4]),
            ('true', fm.GAUSSIAN, [1, 0.4]),
        ],
    )

    fuzzy_rule = FuzzyRules()
    fuzzy_rule.add(
        rule_name='rule1',
        if_term=fuzzy_vars.get('sepal_length')['small']
        & fuzzy_vars.get('sepal_width')['large'],
        then_term=fuzzy_vars.get('setosa')['true'],
    )
    fuzzy_rule.add(
        rule_name='rule2',
        if_term=fuzzy_vars.get('sepal_length')['large']
        & fuzzy_vars.get('sepal_width')['small'],
        then_term=fuzzy_vars.get('setosa')['false'],
    )
    fuzzy_rule.add(
        rule_name='rule3',
        if_term=fuzzy_vars.get('sepal_length')['large']
        & fuzzy_vars.get('sepal_width')['small'],
        then_term=fuzzy_vars.get('non_setosa')['true'],
    )
    fuzzy_rule.add(
        rule_name='rule4',
        if_term=fuzzy_vars.get('sepal_length')['small']
        & fuzzy_vars.get('sepal_width')['large'],
        then_term=fuzzy_vars.get('non_setosa')['false'],
    )

    modeler = FuzzyModeler()
    return modeler.build_model(fuzzy_vars, fuzzy_rule)


def load_data():
    df_raw = datasets.load_iris(as_frame=True).frame
    df_raw.columns = [
        'sepal_length',
        'sepal_width',
        'petal_length',
        'petal_width',
        'species',
    ]
    df_raw['species'] = df_raw['species'].apply(lambda x: 1 if x == 0 else 0)

    # randomly split training and testing dataset
    example_test_data_ratio = 0.4
    df_raw = df_raw.sample(frac=1, random_state=7).reset_index(drop=True)
    n = df_raw.shape[0]
    n_test = int(n * example_test_data_ratio)
    training_data = df_raw.iloc[n_test:, :].reset_index(drop=True)
    test_data = df_raw.iloc[:n_test, :].reset_index(drop=True)

    # make multi-label
    training_data_y = pd.concat(
        [
            training_data['species'].rename('setosa'),
            training_data['species'].apply(lambda x: x ^ 1).rename('non_setosa'),
        ],
        axis=1,
    )
    test_data_y = pd.concat(
        [
            test_data['species'].rename('setosa'),
            test_data['species'].apply(lambda x: x ^ 1).rename('non_setosa'),
        ],
        axis=1,
    )

    return {
        'training_data': {
            'X': training_data[['sepal_length', 'sepal_width']],
            'y': training_data_y,
        },
        'test_data': {
            'X': test_data[['sepal_length', 'sepal_width']],
            'y': test_data_y,
        },
    }


class TestOracle:
    def test_old_oracle_class(self):
        data = load_data()
        modeler = OracleModeler(Oracle)
        model = modeler.build_model(
            data={'unlabeled_data': data['training_data']['X']}, teacher_model=RuleModel
        )

        prediction = model.predict(data['test_data'])['predictions']

        assert len(prediction['setosa']) == len(data['test_data']['y'])

        with tempfile.TemporaryDirectory() as path:
            os.environ['H1ST_MODEL_REPO_PATH'] = path
            version = model.persist()

            loaded_model = Oracle().load(version)

            assert 'sklearn' in str(type(loaded_model.students['setosa'][0].base_model))
            new_prediction = loaded_model.predict(data['test_data'])['predictions']
            pred_df = pd.DataFrame(
                {'old': prediction['setosa'], 'new': new_prediction['setosa']}
            )
            assert len(pred_df[pred_df['old'] != pred_df['new']]) == 0

    def test_rule_based_ensemble_one_student(self):
        data = load_data()
        modeler = OracleModeler()
        model = modeler.build_model(
            data={'unlabeled_data': data['training_data']['X']},
            teacher_model=RuleModel,
            student_modelers=RandomForestModeler,
            ensembler_modeler=RuleBasedModeler(MajorityVotingEnsembleModel),
        )

        prediction = model.predict(data['test_data'])['predictions']

        assert len(prediction['setosa']) == len(data['test_data']['y'])

        with tempfile.TemporaryDirectory() as path:
            os.environ['H1ST_MODEL_REPO_PATH'] = path
            version = model.persist()

            loaded_model = Oracle().load(version)

            assert 'sklearn' in str(type(loaded_model.students['setosa'][0].base_model))
            new_prediction = loaded_model.predict(data['test_data'])['predictions']
            pred_df = pd.DataFrame(
                {'old': prediction['setosa'], 'new': new_prediction['setosa']}
            )
            assert len(pred_df[pred_df['old'] != pred_df['new']]) == 0

    def test_rule_based_ensemble_multiple_students(self):
        data = load_data()
        modeler = OracleModeler()
        model = modeler.build_model(
            data={'unlabeled_data': data['training_data']['X']},
            teacher_model=RuleModel,
            student_modelers=[RandomForestModeler, LogisticRegressionModeler],
            ensembler_modeler=RuleBasedModeler(MajorityVotingEnsembleModel),
        )

        prediction = model.predict(data['test_data'])['predictions']
        assert len(prediction['setosa']) == len(data['test_data']['y'])
        assert any(prediction['setosa'] != data['test_data']['y'])

        with tempfile.TemporaryDirectory() as path:
            os.environ['H1ST_MODEL_REPO_PATH'] = path
            version = model.persist()

            loaded_model = Oracle().load(version)

            assert 'sklearn' in str(type(loaded_model.students['setosa'][0].base_model))
            new_prediction = loaded_model.predict(data['test_data'])['predictions']
            pred_df = pd.DataFrame(
                {'old': prediction['setosa'], 'new': new_prediction['setosa']}
            )
            assert len(pred_df[pred_df['old'] != pred_df['new']]) == 0

    def test_ml_ensemble(self):
        data = load_data()
        new_data = {
            'unlabeled_data': data['training_data']['X'],
            'labeled_data': {
                'X_train': data['training_data']['X'],
                'y_train': data['training_data']['y'],
                'X_test': data['test_data']['X'],
                'y_test': data['test_data']['y'],
            },
        }
        modeler = OracleModeler()
        model = modeler.build_model(
            data=new_data,
            teacher_model=RuleModel,
            ensembler_modeler=MLPEnsembleModeler,
        )

        prediction = model.predict(data['test_data'])['predictions']
        assert len(prediction['setosa']) == len(data['test_data']['y'])

        with tempfile.TemporaryDirectory() as path:
            os.environ['H1ST_MODEL_REPO_PATH'] = path
            version = model.persist()

            loaded_model = Oracle().load(version)

            assert 'sklearn' in str(type(loaded_model.students['setosa'][0].base_model))
            new_prediction = loaded_model.predict(data['test_data'])['predictions']
            pred_df = pd.DataFrame(
                {'old': prediction['setosa'], 'new': new_prediction['setosa']}
            )
            assert len(pred_df[pred_df['old'] != pred_df['new']]) == 0

    def test_rule_based_ensemble_fuzzy_teacher_multiple_students(self):
        data = load_data()
        fuzzy_model = build_fuzzy_model(data)

        modeler = OracleModeler()
        model = modeler.build_model(
            data={'unlabeled_data': data['training_data']['X']},
            teacher_model=fuzzy_model,
            fuzzy_thresholds={'setosa': 0.6, 'non_setosa': 0.49},
            ensembler_modeler=RuleBasedModeler(MajorityVotingEnsembleModel),
        )

        prediction = model.predict(data['test_data'])['predictions']
        assert len(prediction['setosa']) == len(data['test_data']['y'])
        assert any(prediction['setosa'] != data['test_data']['y'])

        with tempfile.TemporaryDirectory() as path:
            os.environ['H1ST_MODEL_REPO_PATH'] = path
            version = model.persist()

            loaded_model = Oracle().load(version)

            assert 'sklearn' in str(type(loaded_model.students['setosa'][0].base_model))
            new_prediction = loaded_model.predict(data['test_data'])['predictions']
            pred_df = pd.DataFrame(
                {'old': prediction['setosa'], 'new': new_prediction['setosa']}
            )
            assert len(pred_df[pred_df['old'] != pred_df['new']]) == 0

    def test_ml_ensemble_fuzzy_teacher(self):
        data = load_data()
        fuzzy_model = build_fuzzy_model(data)
        new_data = {
            'unlabeled_data': data['training_data']['X'],
            'labeled_data': {
                'X_train': data['training_data']['X'],
                'y_train': data['training_data']['y'],
                'X_test': data['test_data']['X'],
                'y_test': data['test_data']['y'],
            },
        }
        modeler = OracleModeler()
        model = modeler.build_model(
            data=new_data,
            teacher_model=fuzzy_model,
            fuzzy_thresholds={'setosa': 0.6, 'non_setosa': 0.49},
            ensembler_modeler=MLPEnsembleModeler,
        )

        prediction = model.predict(data['test_data'])['predictions']
        assert len(prediction['setosa']) == len(data['test_data']['y'])

        with tempfile.TemporaryDirectory() as path:
            os.environ['H1ST_MODEL_REPO_PATH'] = path
            version = model.persist()

            loaded_model = Oracle().load(version)

            assert 'sklearn' in str(type(loaded_model.students['setosa'][0].base_model))
            new_prediction = loaded_model.predict(data['test_data'])['predictions']
            pred_df = pd.DataFrame(
                {'old': prediction['setosa'], 'new': new_prediction['setosa']}
            )
            assert len(pred_df[pred_df['old'] != pred_df['new']]) == 0
