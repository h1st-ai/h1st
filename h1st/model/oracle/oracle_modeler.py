from inspect import isclass
from loguru import logger
from typing import List

from h1st.model.ml_modeler import MLModeler
from h1st.model.modeler import Modeler
from h1st.model.model import Model
from h1st.model.fuzzy import FuzzyModel
from h1st.model.oracle.oracle_model import OracleModel
from h1st.model.oracle.student_modelers import (
    LogisticRegressionModeler,
    RandomForestModeler,
)
from h1st.model.oracle.ensemble_models import MajorityVotingEnsembleModel
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
        student_modelers: List[Modeler] = [RandomForestModeler, LogisticRegressionModeler],
        ensembler_modeler: Modeler = RuleBasedModeler(MajorityVotingEnsembleModel),
        **kwargs
    ) -> Model:
        '''
        Build the components of Oracle, which are students and ensemblers.
        student is always MLModel and ensembler can be MLModel or RuleBasedModel.
        :param data: dictionary with data to build Oracle model
        :param teacher: an Instance of Model as the teacher
        :param students: a list of Modeler Class to act as students
        :param ensembler: an Instance or a Class of Modeler to act as the ensemble
        :param fuzzy_thresholds: optional param to be used when teacher is an instance of FuzzyModel
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
        if isinstance(teacher_model, FuzzyModel) and kwargs.get('fuzzy_thresholds') is None:
            raise ValueError(
                'Should provide fuzzy_thresholds when using FuzzyModel teacher'
            )
        
        for modeler in student_modelers:
            if not isinstance(modeler, MLModeler):
                raise ValueError('Student modeler should be MLModeler')

        if not isinstance(ensembler_modeler, Modeler):
            raise TypeError('Ensembler should be a Modeler')
        if isinstance(ensembler_modeler, MLModeler) and data.get('labeled_data') is None:
            raise ValueError('Should provide labeled data to train ML based ensembler')

        self.stats['fuzzy_thresholds'] = kwargs.get('fuzzy_thresholds')
        self.stats['features'] = kwargs.get('features')
        self.stats['inject_x_in_ensembler'] = kwargs.get('inject_x_in_ensembler', False)

        teacher_predictions = self.generate_teacher_predictions(
            data=data, teacher=teacher_model, kwargs=kwargs
        )
        student_models = self.train_students(
            data=data, modelers=student_modelers, teacher_predictions=teacher_predictions
        )
        ensemble_models = self.train_ensembles(
            data=data, modeler=ensembler_modeler, teacher_predictions=teacher_predictions
        )
        
        oracle_model = self.model_class(
            teacher=teacher_model, students=student_models, ensemblers=ensemble_models
        )

        return oracle_model

    def generate_teacher_predictions(
        self, data: dict, teacher: Model, **kwargs
    ) -> dict:
        '''
        Generate teacher's prediction which will be used as y value of students' training data.
        '''
        result = self.model_class.generate_teacher_predictions(
            data={'X': data['unlabeled_data']}, teacher=teacher
        )

        # If teacher is FuzzyModel, convert float to zero or one to use this as y value.
        if isinstance(teacher, FuzzyModel) or issubclass(teacher.__class__, FuzzyModel):
            for k, v in kwargs['fuzzy_thresholds'].items():
                result[k] = list(map(lambda y: 1 if y > v else 0, result[k]))

        self.stats['labels'] = [col for col in result]
        return result

    def train_students(
        self, data: dict, modelers: List[Modeler], teacher_predictions: dict
    ) -> dict:
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

    def train_ensembles(self, data: dict, modeler: Modeler, teacher_predictions: dict) -> dict:
        '''
        Build one ensembler per label of teacher output (M labels).
        There will be M ensemblers in total.
        '''
        labeled_data = data.get('labeled_data')
        if not labeled_data:
            train_data = {label: None for label in teacher_predictions}
        

        result = {}
        for label in train_data:
            result[label] = modeler.build_model(train_data[label])
        
        return result
