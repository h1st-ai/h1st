"""Fault Prediction Oracle."""


from __future__ import annotations

from typing import List, Sequence, Tuple   # Py3.9+: use built-ins

from pandas import DataFrame, Series

from h1st.utils.data_proc import ParquetDataset

from h1st.contrib.pmfp.models.base import BaseFaultPredictor
from .teacher.base import BaseFaultPredTeacher
from .student.timeseries_dl import (TimeSeriesDLFaultPredStudentModeler,
                                    TimeSeriesDLFaultPredStudent)
from .ensemble.basic import EitherFaultPredEnsemble


class FaultPredOracleModeler:
    """Fault Prediction Oracle Modeler."""

    def __init__(self, teacher: BaseFaultPredTeacher,

                 student_input_cat_cols: Sequence[str],
                 student_input_num_cols: Sequence[str],
                 student_input_subsampling_factor: int,
                 student_input_n_rows_per_day: int,

                 student_train_date_range: Tuple[str, str],
                 student_tuning_date_range: Tuple[str, str]):
        # pylint: disable=super-init-not-called
        """Init Fault Prediction Oracle Modeler."""
        self.teacher: BaseFaultPredTeacher = teacher

        self.student_input_cat_cols: Sequence[str] = student_input_cat_cols
        self.student_input_num_cols: Sequence[str] = student_input_num_cols
        self.student_input_subsampling_factor: int = student_input_subsampling_factor   # noqa: E501
        self.student_input_n_rows_per_day: int = student_input_n_rows_per_day

        self.student_train_date_range: Tuple[str, str] = student_train_date_range   # noqa: E501
        self.student_tuning_date_range: Tuple[str, str] = student_tuning_date_range   # noqa: E501

    def build_model(self) -> FaultPredOracle:
        """Construct an Oracle from a Knowledge ("Teacher") Model."""
        # train Knowledge Generalizer ("Student") model
        student: TimeSeriesDLFaultPredStudent = \
            TimeSeriesDLFaultPredStudentModeler(
                teacher=self.teacher,
                input_cat_cols=self.student_input_cat_cols,
                input_num_cols=self.student_input_num_cols,
                input_subsampling_factor=self.student_input_subsampling_factor,
                input_n_rows_per_day=self.student_input_n_rows_per_day,
                date_range=self.student_train_date_range).build_model()

        # tune Knowledge Generalizer ("Student") model's decision threshold
        student.tune_decision_threshold(
            tuning_date_range=self.student_tuning_date_range)


class FaultPredOracle(BaseFaultPredictor):
    # pylint: disable=abstract-method,too-many-ancestors
    """Fault Prediction Oracle."""

    def __init__(self,
                 teacher: BaseFaultPredTeacher,
                 student: TimeSeriesDLFaultPredStudent,
                 ensemble: EitherFaultPredEnsemble = EitherFaultPredEnsemble()):  # noqa: E501
        """Init Fault Prediction Oracle."""
        super().__init__(general_type=teacher.general_type,
                         unique_type_group=teacher.unique_type_group,
                         version=student.version)

        self.teacher: BaseFaultPredTeacher = teacher
        self.student: TimeSeriesDLFaultPredStudent = student
        self.ensemble: EitherFaultPredEnsemble = ensemble

    @classmethod
    def load(cls, version: str) -> FaultPredOracle:
        """Load oracle by version."""
        # pylint: disable=import-error,import-outside-toplevel
        import ai.models

        teacher_name, _student_name = version.split('---')

        teacher_class_name, teacher_version = teacher_name.split('--')
        teacher_class = getattr(ai.models, teacher_class_name)
        teacher: BaseFaultPredTeacher = teacher_class.load(version=teacher_version)   # noqa: E501

        student: TimeSeriesDLFaultPredStudent = \
            TimeSeriesDLFaultPredStudent.load(version=version)

        return cls(teacher=teacher, student=student)

    @classmethod
    def list_versions(cls) -> List[str]:
        """List model versions."""
        return TimeSeriesDLFaultPredStudent.list_versions()

    def predict(self,
                df_for_1_equipment_unit_for_1_day: DataFrame, /) \
            -> Tuple[bool, bool, bool]:
        """Make oracle prediction."""
        return (
            teacher_pred := self.teacher.predict(df_for_1_equipment_unit_for_1_day),   # noqa: E501
            student_pred := self.student.predict(df_for_1_equipment_unit_for_1_day,   # noqa: E501
                                                 return_binary=True),
            self.ensemble.predict(teacher_pred=teacher_pred,
                                  student_pred=student_pred))

    def batch_predict(self, parquet_ds: ParquetDataset) -> Series:
        """Batch-Predict faults."""
        return Series(
            data=zip(
                teacher_preds := self.teacher.batch_predict(parquet_ds),
                student_preds := self.student.batch_predict(parquet_ds,
                                                            return_binary=True),   # noqa: E501
                ensemble_preds := self.ensemble.batch_predict(
                    teacher_preds=teacher_preds, student_preds=student_preds)),
            index=ensemble_preds.index,
            dtype=None, name='FAULT', copy=False, fastpath=False)
