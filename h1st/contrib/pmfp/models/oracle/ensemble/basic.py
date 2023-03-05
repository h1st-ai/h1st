"""Basic heuristics-based Ensembles."""


from pandas import Series


__all__ = 'EitherFaultPredEnsemble', 'UnanimousFaultPredEnsemble'


class EitherFaultPredEnsemble:
    # pylint: disable=too-many-ancestors
    """Either K ("Teacher") or K-Gen ("Student") model predicts fault."""

    @staticmethod
    def predict(teacher_pred: bool, student_pred: bool) -> bool:
        """Either K ("Teacher") or K-Gen ("Student") model predicts fault."""
        return teacher_pred or student_pred

    @staticmethod
    def batch_predict(teacher_preds: Series, student_preds: Series) -> Series:
        """Either K ("Teacher") or K-Gen ("Student") model predicts fault."""
        assert (teacher_preds.index == student_preds.index).all()
        return teacher_preds | student_preds


class UnanimousFaultPredEnsemble:
    # pylint: disable=too-many-ancestors
    """Unanimous vote between K ("Teacher") & K-Gen ("Student") models."""

    @staticmethod
    def predict(teacher_pred: bool, student_pred: bool) -> bool:
        """Unanimous vote between K ("Teacher") & K-Gen ("Student") models."""
        return teacher_pred and student_pred

    @staticmethod
    def batch_predict(teacher_preds: Series, student_preds: Series) -> Series:
        """Unanimous votes between K ("Teacher") & K-Gen ("Student") models."""
        assert (teacher_preds.index == student_preds.index).all()
        return teacher_preds & student_preds
