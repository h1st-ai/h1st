import pandas as pd

from inspect import isclass
from loguru import logger
from typing import List, Dict

from h1st.model.ml_modeler import MLModeler
from h1st.model.modeler import Modeler
from h1st.model.model import Model
from h1st.model.fuzzy import FuzzyModel
from h1st.model.oracle.oracle_model import OracleModel
from h1st.model.oracle.student_modelers import (
    LogisticRegressionModeler,
    RandomForestModeler,
)
from h1st.model.oracle.ensembler_models import MajorityVotingEnsembleModel
from h1st.model.rule_based_model import RuleBasedModel
from h1st.model.rule_based_modeler import RuleBasedModeler


# TODO: fuzzy model output is now like [0.2, 0.5, 0.4, 0.7]
# TODO: we can build multiple binary classifier or one multi-class classifier
# TODO: if student is multiple binary classifier, then ensemble also should be like that ?


class OracleModeler(Modeler):
    '''
    Modeler to build an Oracle model with a Model as the teacher,
    a list of Modeler as students and a list of Modeler as ensemblers.
    User can provide additional information like labeled data or fuzzy threshold to build model
    '''

    def __init__(self, model_class=None):
        self.stats = {}
        if model_class is None:
            self.model_class = OracleModel
        else:
            self.model_class = model_class

    def build_model(
        self,
        data: dict = None,
        teacher_model: Model = RuleBasedModel,
        student_modelers: List[Modeler] = [
            RandomForestModeler,
            LogisticRegressionModeler,
        ],
        ensembler_modeler: Modeler = RuleBasedModeler(MajorityVotingEnsembleModel),
        **kwargs,
    ) -> Model:
        '''
        Build the components of Oracle, which are students and ensemblers.
        student is always MLModel and ensembler can be MLModel or RuleBasedModel.
        :param data: dictionary with data to build Oracle model
        :param teacher_model: a Model as the teacher
        :param student_modelers: a list of Modeler Class to act as students
        :param ensembler_modeler: a Modeler to act as the ensembler
        :param fuzzy_thresholds: optional param to be used when teacher is an instance of FuzzyModel
        :param features: option param to used as feature to gen teacher prediction
        :return: a model which Class depends on OracleModeler init call, default is OracleModel
        '''
        if isclass(teacher_model):
            teacher_model = teacher_model()
        if isclass(ensembler_modeler):
            ensembler_modeler = ensembler_modeler()

        if not isinstance(student_modelers, list):
            student_modelers = [student_modelers]
        tmp_students = []
        for modeler in student_modelers:
            if isclass(modeler):
                modeler = modeler()
            tmp_students.append(modeler)
        student_modelers = tmp_students

        if not isinstance(teacher_model, Model):
            raise TypeError('Teacher should be a Model ')
        if (
            isinstance(teacher_model, FuzzyModel)
            and kwargs.get('fuzzy_thresholds') is None
        ):
            raise ValueError(
                'Should provide fuzzy_thresholds when using FuzzyModel teacher'
            )

        for modeler in student_modelers:
            if not isinstance(modeler, MLModeler):
                raise ValueError('Student modeler should be MLModeler')

        if not isinstance(ensembler_modeler, Modeler):
            raise TypeError('Ensembler should be a Modeler')
        if (
            isinstance(ensembler_modeler, MLModeler)
            and data.get('labeled_data') is None
        ):
            raise ValueError('Should provide labeled data to train ML based ensembler')

        self.stats['fuzzy_thresholds'] = kwargs.get('fuzzy_thresholds')
        self.stats['features'] = kwargs.get('features')
        self.stats['inject_x_in_ensembler'] = kwargs.get('inject_x_in_ensembler', False)

        teacher_predictions = self.generate_teacher_predictions(
            data=data, model=teacher_model, **kwargs
        )
        student_models = self.train_students(
            data=data,
            modelers=student_modelers,
            teacher_predictions=teacher_predictions,
        )
        ensemble_models = self.train_ensemblers(
            data=data,
            modeler=ensembler_modeler,
            teacher_predictions=teacher_predictions,
            teacher=teacher_model,
            students=student_models,
        )

        oracle_model = self.model_class(
            teacher=teacher_model, students=student_models, ensemblers=ensemble_models
        )

        return oracle_model

    def generate_teacher_predictions(self, data: dict, model: Model, **kwargs) -> dict:
        '''
        Generate teacher's prediction which will be used as y value of students' training data.
        '''
        result = self.model_class.generate_teacher_predictions(
            data={'X': data['unlabeled_data']}, teacher=model, features=kwargs.get('features')
        )

        # If teacher is FuzzyModel, convert float to zero or one to use this as y value.
        if isinstance(model, FuzzyModel) or issubclass(model.__class__, FuzzyModel):
            for k, v in kwargs['fuzzy_thresholds'].items():
                result[k] = list(map(lambda y: 1 if y > v else 0, result[k]))

        self.stats['labels'] = [col for col in result]
        return result

    def train_students(
        self, data: dict, modelers: List[Modeler], teacher_predictions: dict
    ) -> Dict[str, List[Model]]:
        '''
        Build one binary classifier (from each student modeler) per label of teacher output.
        If there are N number of student_modelers and M number of teacher output labels,
        then the total number of student models is N * M.
        '''
        result = {}
        for label in teacher_predictions:
            train_data = {'X': data['unlabeled_data'], 'y': teacher_predictions[label]}

            tmp_array = []
            for modeler in modelers:
                model = modeler.build_model(train_data)
                tmp_array.append(model)
            result[label] = tmp_array

        return result

    def train_ensemblers(
        self,
        data: dict,
        modeler: Modeler,
        teacher_predictions: dict,
        teacher: Model,
        students=Dict[str, List[Model]],
    ) -> Dict[str, List[Model]]:
        '''
        Build one ensembler per label of teacher output (M labels).
        There will be M ensemblers in total.
        '''
        labeled_data = data.get('labeled_data')
        if not labeled_data:
            train_data = {label: None for label in teacher_predictions}
        else:
            train_data = self._generate_ensembler_training_data(
                labeled_data=labeled_data,
                teacher=teacher,
                students=students,
                ensembler_modeler=modeler,
            )

        result = {}
        for label in train_data:
            result[label] = modeler.build_model(train_data[label])

        return result

    def _generate_ensembler_training_data(
        self,
        labeled_data: dict,
        teacher: Model,
        students: Dict[str, List[Model]],
        ensembler_modeler: Modeler,
    ) -> dict:
        result = {}
        x_train_input = {'X': labeled_data['X_train']}
        x_test_input = {'X': labeled_data['X_test']}

        # Generate teacher predictions
        teacher_preds_train = self.model_class.generate_teacher_predictions(
            x_train_input, teacher, features=self.stats['features']
        )
        teacher_preds_test = self.model_class.generate_teacher_predictions(
            x_test_input, teacher, features=self.stats['features']
        )

        for label in teacher_preds_train:
            # Generate student predictions
            student_preds_train_data = []
            student_preds_test_data = []
            for idx, student in enumerate(students[label]):
                predict_proba = getattr(student, 'predict_proba', None)
                if callable(predict_proba) and isinstance(ensembler_modeler, MLModeler):
                    s_pred_train = predict_proba(x_train_input)['predictions'][:, 0]
                    s_pred_test = predict_proba(x_test_input)['predictions'][:, 0]
                else:
                    s_pred_train = student.predict(x_train_input)['predictions']
                    s_pred_test = student.predict(x_test_input)['predictions']

                student_preds_train_data.append(
                    pd.Series(
                        s_pred_train,
                        name=f'stud_{label}_{idx}',
                    )
                )
                student_preds_test_data.append(
                    pd.Series(
                        s_pred_test,
                        name=f'stud_{label}_{idx}',
                    ),
                )

            # Create training data of ensembler
            ensembler_train_input = [
                teacher_preds_train[label]
            ] + student_preds_train_data
            ensembler_test_input = [teacher_preds_test[label]] + student_preds_test_data

            # Inject original x value into input feature of Ensembler
            if (
                isinstance(ensembler_modeler, MLModeler)
                and (
                    isinstance(x_train_input['X'], pd.DataFrame)
                    or isinstance(x_train_input['X'], pd.Series)
                )
                and self.stats['inject_x_in_ensembler']
            ):
                ensembler_train_input += [x_train_input['x'].reset_index(drop=True)]
                ensembler_test_input += [x_test_input['x'].reset_index(drop=True)]

            result[label] = {
                'X_train': pd.concat(ensembler_train_input, axis=1).values,
                'y_train': labeled_data['y_train'][label].reset_index(drop=True)
                if isinstance(labeled_data['y_train'], pd.DataFrame)
                else labeled_data['y_train'],
                'X_test': pd.concat(ensembler_test_input, axis=1).values,
                'y_test': labeled_data['y_test'][label].reset_index(drop=True)
                if isinstance(labeled_data['y_test'], pd.DataFrame)
                else labeled_data['y_test'],
            }

        return result
