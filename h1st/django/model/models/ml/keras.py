from ....util import PGSQL_IDENTIFIER_MAX_LEN
from ...apps import H1stModelModuleConfig
from .base import H1stMLModel


class KerasModel(H1stMLModel):
    class Meta(H1stMLModel.Meta):
        verbose_name = 'H1st Keras Model'
        verbose_name_plural = 'H1st Keras Models'

        db_table = \
            f"{H1stModelModuleConfig.label}_{__qualname__.split('.')[0]}"
        assert len(db_table) <= PGSQL_IDENTIFIER_MAX_LEN, \
            ValueError(f'*** "{db_table}" DB TABLE NAME TOO LONG ***')

        default_related_name = 'h1st_keras_models'


# alias
H1stKerasModel = KerasModel
