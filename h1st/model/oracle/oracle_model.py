import pandas as pd
from typing import Dict, List

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

    def persist(self, version=None) -> str:
        student_details = {}
        ensembler_details = {}
        for label in self.stats['labels']:
            student_classes = []
            student_versions = []
            index = 0
            for model in self.students[label]:
                student_classes.append(model.__class__)
                version = model.persist(f'student_{version}_{label}_{index}')
                student_versions.append(version)
                index += 1

            student_details[label] = {
                'class': student_classes,
                'version': student_versions,
            }

            ensembler_version = self.ensemblers[label].persist(
                f'ensembler_{version}_{label}'
            )
            ensembler_details[label] = {
                'class': self.ensemblers[label].__class__,
                'version': ensembler_version,
            }

        teacher_version = self.teacher.persist(f'teacher_{version}')
        model_details = {
            'teacher_details': {
                'class': self.teacher.__class__,
                'version': teacher_version,
            },
            'student_details': student_details,
            'ensembler_details': ensembler_details,
        }
        self.stats['model_details'] = model_details

        super().persist(version)
        return version

    def load(self, version: str = None) -> Model:
        super().load(version)
        model_details = self.stats['model_details']

        teacher_model = model_details['teacher_details']['class']
        teacher_version = model_details['teacher_details']['version']
        self.teacher = teacher_model().load(teacher_version)

        students = {}
        ensemblers = {}
        for label in self.stats['labels']:
            students[label] = []
            for stud_class, stud_version in zip(
                model_details['student_details'][label]['class'],
                model_details['student_details'][label]['version'],
            ):
                student_model = stud_class().load(stud_version)
                students[label].append(student_model)

            ensembler_class = model_details['ensembler_details'][label]['class']
            ensembler_version = model_details['ensembler_details'][label]['version']
            ensemblers[label] = ensembler_class().load(ensembler_version)

        self.students = students
        self.ensemblers = ensemblers

        return self

    # Keep it for backward compatibility. It will be deprecated in the future.
    def load_params(self, version: str = None) -> Model:
        return self.load(version)
