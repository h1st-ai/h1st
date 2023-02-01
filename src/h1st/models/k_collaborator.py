from loguru import logger
from typing import List

from h1st.models.model import Model


class KCollaborator(Model):
    def __init__(
        self, 
        data: dict = None, 
        knowledge_models: List[Model] = None,
        ml_models: List[Model] = None,
        ensemble: Model = None
    ) -> None:
        self.knowledge_models = knowledge_models
        self.ml_models = ml_models
        self.ensemble = ensemble

        if all(param is not None for param in [data, knowledge_models, ml_models, ensemble]):
            logger.info('Trigger auto-train!')
            self.train(data)

    def train(self, data: dict) -> None:
        pass

    def predict(self, data: dict) -> dict:
        if not self.is_trained:
            logger.error('Model is not trained')
            raise RuntimeError('Model is not trained')

        return {}
