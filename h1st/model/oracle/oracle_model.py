import pandas as pd
from typing import Dict, List
from loguru import logger

from h1st.model.model import Model
from h1st.model.predictive_model import PredictiveModel


class OracleModel(PredictiveModel):
    def __init__(
        self,
        teacher: Model = None,
        students: Dict[str, List[Model]] = None,
        ensemblers: Dict[str, Model] = None,
    ):
        self.teacher = teacher
        self.students = students
        self.ensemblers = ensemblers
        self.stats = {}

    @classmethod
    def generate_teacher_predictions(cls, data: dict, teacher: Model, **kwargs) -> dict:
        '''
        Generate the predictions of teacher for the given data.
        Override this function to implement custom data generation.
        @param data: unlabelled data in dictionary with key `X`
        @param teacher: an Instance of Boolean or Fuzzy rule-based model
        @param features: optional to choose list of features to be used in teacher prediction
        @return: a dictionary of features and teacher's prediction.
        '''
        if 'X' not in data:
            raise KeyError("Please provide data in form of {'X': pd.DataFrame}")

        df = data['X']
        if kwargs.get('features') is not None:
            df = df[kwargs['features']]

        result = teacher.predict({'X': df})

        if 'predictions' not in result:
            raise KeyError("Teacher's output must contain a key named `predictions`")
        return result['predictions']

    def predict(self, input_data: Dict) -> Dict:
        '''
        Implement logic to generate prediction from data.
        The Oracle expects the same features provided during `build` phase to be in the provided data.
        It automatically process the data the same way to that of the `build` phase.
        :params input_data: an dictionary with key `X` containing the data to get predictions.
        :returns: a dictionary with key `predictions` containing the predictions
        '''
        if not self.students:
            raise RuntimeError('No student build')
        if not self.ensemblers:
            raise RuntimeError('No ensembler built')

        result = {}

        teacher_predictions = self.generate_teacher_predictions(
            data=input_data, teacher=self.teacher
        )
        for label in teacher_predictions:
            student_predictions = []
            index = 0
            for model in self.students[label]:
                prediction = model.predict(input_data)['predictions']
                student_predictions.append(
                    pd.Series(prediction, name=f'stud_{label}_{index}')
                )
                index += 1

            ensembler_input = [teacher_predictions[label]] + student_predictions
            ensembler_input = pd.concat(ensembler_input, axis=1)

            ensembler = self.ensemblers[label]
            result[label] = ensembler.predict({'X': ensembler_input})['predictions']

        self.stats['labels'] = list(teacher_predictions.keys())
        result = pd.DataFrame(result)
        return {'predictions': result}

    def persist(self, version: str = None) -> str:
        teacher_details = self._persist_teacher(version)
        student_details = self._persist_students(version)
        ensembler_details = self._persist_ensemblers(version)

        model_details = {
            'teacher_details': teacher_details,
            'student_details': student_details,
            'ensembler_details': ensembler_details,
        }
        self.stats['model_details'] = model_details

        super().persist(version)
        return version

    def _persist_teacher(self, version: str = None) -> dict:
        teacher_version = self.teacher.persist(f'teacher_{version}')
        return {
            'class': self.teacher.__class__,
            'version': teacher_version,
        }

    def _persist_students(self, version: str = None) -> dict:
        details = {}
        for label in self.stats['labels']:
            student_classes = []
            student_versions = []
            index = 0
            for model in self.students[label]:
                student_classes.append(model.__class__)
                student_version = model.persist(f'student_{version}_{label}_{index}')
                student_versions.append(student_version)
                index += 1

            details[label] = {
                'class': student_classes,
                'version': student_versions,
            }

        return details

    def _persist_ensemblers(self, version: str = None) -> dict:
        details = {}
        for label in self.stats['labels']:
            ensembler_version = self.ensemblers[label].persist(
                f'ensembler_{version}_{label}'
            )
            details[label] = {
                'class': self.ensemblers[label].__class__,
                'version': ensembler_version,
            }

        return details

    def load(self, version: str = None) -> Model:
        super().load(version)
        model_details = self.stats['model_details']

        self._load_teacher(details=model_details['teacher_details'])
        self._load_students(details=model_details['student_details'])
        self._load_ensemblers(details=model_details['ensembler_details'])

        return self

    def _load_teacher(self, details: dict) -> None:
        model = details['class']
        version = details['version']
        self.teacher = model().load(version)

    def _load_students(self, details: dict) -> None:
        students = {}
        for label in self.stats['labels']:
            students[label] = []
            for cls, version in zip(
                details[label]['class'], details[label]['version']
            ):
                model = cls().load(version)
                students[label].append(model)
        self.students = students

    def _load_ensemblers(self, details: dict) -> None:
        ensemblers = {}
        for label in self.stats['labels']:
            model = details[label]['class']
            version = details[label]['version']
            ensemblers[label] = model().load(version)
        self.ensemblers = ensemblers

    # Keep it for backward compatibility. It will be deprecated in the future.
    def load_params(self, version: str = None) -> Model:
        return self.load(version)
