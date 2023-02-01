from loguru import logger
from typing import List

from h1st.models.model import Model


class KOracle:
    DEFAULT_TEACHER = Model
    DEFAULT_STUDENTS = [Model]
    DEFAULT_ENSEMBLE = Model

    def __init__(
        self, 
        data: dict = None, 
        teacher: Model = None, 
        students: List[Model] = None, 
        ensemble: Model = None,
    ) -> None:
        self.teacher = teacher 
        self.students = students 
        self.ensemble = ensemble

        if all(param is not None for param in [data, teacher, students, ensemble]):
            logger.info('Trigger auto-train!')
            self.train(data)

    def train(self, data: dict) -> None:
        if self.teacher is None:
            logger.error('Teacher need to be provided')
            raise RuntimeError('Teacher need to be provided')

        teacher_prediction = self.teacher.predict(data)
        if self.students is None:
            tmp_list = []
            for model in self.DEFAULT_STUDENTS:
                model_obj = model(teacher_prediction)
                tmp_list.append(model_obj)
            self.students = tmp_list

        if self.ensemble is None:
            self.ensemble = self.DEFAULT_ENSEMBLE()

        self.is_trained = True
        logger.info('Training completed')

    def predict(self, data: dict) -> dict:
        if not self.is_trained:
            logger.error('Model is not trained')
            raise RuntimeError('Model is not trained')

        teacher_prediction = self.teacher.predict(data)
        student_predictions = []
        for model in self.students:
            pred = model.predict(teacher_prediction)
            student_predictions.append(pred)

        ensemble_prediction = self.ensemble.predict(teacher_prediction, student_predictions)
        return ensemble_prediction

    def load(self) -> None:
        pass

    def persist(self) -> None:
        pass
