from h1st.h1flow.h1flow import Graph as _CoreH1stWorkflow

from ...util import PGSQL_IDENTIFIER_MAX_LEN
from ..apps import H1stModelModuleConfig

from .base import H1stModel


class Workflow(H1stModel, _CoreH1stWorkflow):
    class Meta(H1stModel.Meta):
        verbose_name = 'H1st Workflow'
        verbose_name_plural = 'H1st Workflows'

        db_table = \
            f"{H1stModelModuleConfig.label}_{__qualname__.split('.')[0]}"
        assert len(db_table) <= PGSQL_IDENTIFIER_MAX_LEN, \
            ValueError(f'*** "{db_table}" DB TABLE NAME TOO LONG ***')

        default_related_name = 'h1st_workflows'

    def predict(self, *args, **kwargs):
        return _CoreH1stWorkflow.predict(self, *args, **kwargs)


# alias
H1stWorkflow = Workflow
