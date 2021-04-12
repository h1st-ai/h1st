from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.deletion import PROTECT
from django.db.models.fields import CharField
from django.db.models.fields.json import JSONField
from django.db.models.fields.related import ForeignKey

from json.decoder import JSONDecoder

from ..model.models import H1stModel
from ..util import PGSQL_IDENTIFIER_MAX_LEN
from ..util.git import get_git_repo_head_commit_hash
from ..util.models import _ModelWithUUIDPKAndTimestamps
from ..util.pip import get_python_dependencies
from .apps import H1stTrustModuleConfig


class Decision(_ModelWithUUIDPKAndTimestamps):
    RELATED_NAME = 'decisions'
    RELATED_QUERY_NAME = 'decision'

    input_data = \
        JSONField(
            verbose_name='Input Data into Decision',
            help_text='Input Data into Decision',

            encoder=DjangoJSONEncoder,
            decoder=JSONDecoder,

            null=True,
            blank=True,
            choices=None,
            db_column=None,
            db_index=False,
            db_tablespace=None,
            default=None,
            editable=True,
            # error_messages=None,
            primary_key=False,
            unique=False,
            unique_for_date=None, unique_for_month=None, unique_for_year=None,
            # validators=None
        )

    model = \
        ForeignKey(
            verbose_name='Model producing Decision',
            help_text='Model producing Decision',

            to=H1stModel,
            on_delete=PROTECT,
            limit_choices_to={},
            related_name=RELATED_NAME,
            related_query_name=RELATED_QUERY_NAME,
            # to_field=...,
            db_constraint=True,
            swappable=True,

            null=False,
            blank=False,
            choices=None,
            db_column=None,
            db_index=True,   # implied
            db_tablespace=None,
            default=None,
            editable=True,
            # error_messages=None,
            primary_key=False,
            unique=False,
            unique_for_date=None, unique_for_month=None, unique_for_year=None,
            # validators=None
        )

    model_code = \
        JSONField(
            verbose_name='Code of Model(s) producing Decision',
            help_text='Code of Model(s) producing Decision',

            encoder=DjangoJSONEncoder,
            decoder=JSONDecoder,

            null=False,
            blank=False,
            choices=None,
            db_column=None,
            db_index=False,
            db_tablespace=None,
            default=None,
            editable=True,
            # error_messages=None,
            primary_key=False,
            unique=False,
            unique_for_date=None, unique_for_month=None, unique_for_year=None,
            # validators
        )

    git_repo_head_commit_hash = \
        CharField(
            verbose_name='Git Repository Head Commit Hash',
            help_text='Git Repository Head Commit Hash',

            max_length=40,

            null=True,
            blank=True,
            choices=None,
            db_column=None,
            db_index=True,
            db_tablespace=None,
            default=get_git_repo_head_commit_hash,
            editable=True,
            # error_messages=None,
            primary_key=False,
            unique=False,
            unique_for_date=None, unique_for_month=None, unique_for_year=None,
            # validators
        )

    python_dependencies = \
        JSONField(
            verbose_name='Python Dependencies',
            help_text='Python Dependencies',

            encoder=DjangoJSONEncoder,
            decoder=JSONDecoder,

            null=False,
            blank=False,
            choices=None,
            db_column=None,
            db_index=False,
            db_tablespace=None,
            default=get_python_dependencies,
            editable=True,
            # error_messages=None,
            primary_key=False,
            unique=False,
            unique_for_date=None, unique_for_month=None, unique_for_year=None,
            # validators
        )

    output_data = \
        JSONField(
            verbose_name='Output Data from Decision',
            help_text='Output Data from Decision',

            encoder=DjangoJSONEncoder,
            decoder=JSONDecoder,

            null=True,
            blank=True,
            choices=None,
            db_column=None,
            db_index=False,
            db_tablespace=None,
            default=None,
            editable=True,
            # error_messages=None,
            primary_key=False,
            unique=False,
            unique_for_date=None, unique_for_month=None, unique_for_year=None,
            # validators
        )

    class Meta(_ModelWithUUIDPKAndTimestamps.Meta):
        verbose_name = 'Decision'
        verbose_name_plural = 'Decisions'

        db_table = \
            f"{H1stTrustModuleConfig.label}_{__qualname__.split('.')[0]}"
        assert len(db_table) <= PGSQL_IDENTIFIER_MAX_LEN, \
            ValueError(f'*** "{db_table}" DB TABLE NAME TOO LONG ***')

        default_related_name = 'decisions'

    def __str__(self) -> str:
        return f'{type(self).__name__} #{self.uuid} by {self.model}'


class ModelEvalMetricsSet(_ModelWithUUIDPKAndTimestamps):
    RELATED_NAME = 'model_eval_metrics_sets'
    RELATED_QUERY_NAME = 'model_eval_metrics_set'

    model = \
        ForeignKey(
            verbose_name='Model evaluated',
            help_text='Model evaluated',

            to=H1stModel,
            on_delete=PROTECT,
            limit_choices_to={},
            related_name=RELATED_NAME,
            related_query_name=RELATED_QUERY_NAME,
            # to_field=...,
            db_constraint=True,
            swappable=True,

            null=False,
            blank=False,
            choices=None,
            db_column=None,
            db_index=True,   # implied
            db_tablespace=None,
            default=None,
            editable=True,
            # error_messages=None,
            primary_key=False,
            unique=False,
            unique_for_date=None, unique_for_month=None, unique_for_year=None,
            # validators
        )

    eval_data = \
        JSONField(
            verbose_name='Data for Evaluation',
            help_text='Data for Evaluation',

            encoder=DjangoJSONEncoder,
            decoder=JSONDecoder,

            null=False,
            blank=False,
            choices=None,
            db_column=None,
            db_index=False,
            db_tablespace=None,
            default=None,
            editable=True,
            # error_messages=None,
            primary_key=False,
            unique=False,
            unique_for_date=None, unique_for_month=None, unique_for_year=None,
            # validators
        )

    eval_metrics = \
        JSONField(
            verbose_name='Evaluation Metrics',
            help_text='Evaluation Metrics',

            encoder=DjangoJSONEncoder,
            decoder=JSONDecoder,

            null=False,
            blank=False,
            choices=None,
            db_column=None,
            db_index=False,
            db_tablespace=None,
            default=None,
            editable=True,
            # error_messages=None,
            primary_key=False,
            unique=False,
            unique_for_date=None, unique_for_month=None, unique_for_year=None,
            # validators
        )

    class Meta(_ModelWithUUIDPKAndTimestamps.Meta):
        verbose_name = 'Model Evaluation Metrics Set'
        verbose_name_plural = 'Model Evaluation Metrics Sets'

        db_table = \
            f"{H1stTrustModuleConfig.label}_{__qualname__.split('.')[0]}"
        assert len(db_table) <= PGSQL_IDENTIFIER_MAX_LEN, \
            ValueError(f'*** "{db_table}" DB TABLE NAME TOO LONG ***')

        default_related_name = 'model_eval_metrics_sets'

        ordering = '-model__modified', '-modified'

    def __str__(self) -> str:
        return f'Evaluation Metric Set #{self.uuid} of {self.h1st_model}: ' \
               f'{self.eval_metrics}'
