"""Base Fault Prediction knowledge ("teacher") model class."""


from __future__ import annotations

from random import choice
from typing import Optional

from pandas import DataFrame

from h1st.contrib.pmfp.models.base import BaseFaultPredictor


class BaseFaultPredTeacher(BaseFaultPredictor):
    # pylint: disable=abstract-method
    """Base Fault Prediction knowledge ("teacher") model class."""

    def __init__(self,
                 general_type: str, unique_type_group: str,
                 version: Optional[str] = None):
        """Init Fault Prediction knowledge ("teacher") model."""
        super().__init__(general_type=general_type,
                         unique_type_group=unique_type_group,
                         version=version)

    @classmethod
    def load(cls, version: str) -> BaseFaultPredTeacher:
        """Load model artifacts by persisted model's version."""
        if cls is BaseFaultPredTeacher:
            # return an arbitrary model for testing
            return cls(general_type='refrig',
                       unique_type_group='co2_mid_1_compressor')

        raise NotImplementedError

    def predict(self, df_for_1_equipment_unit_for_1_day: DataFrame, /) -> bool:
        """Fault Prediction logic.

        User shall override this method and return a boolean value indicating
        whether the equipment unit has the concerned fault on the date.
        """
        return choice((False, True))
