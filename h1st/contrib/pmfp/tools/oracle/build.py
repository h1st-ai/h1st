"""Oraclize a Fault-Prediction Knowledge ("Teacher") model.

Example:
AWS_ACCESS_KEY_ID=<...aws-access-key-id...> \
AWS_SECRET_ACCESS_KEY=<...aws-secret-access-key...> \
    \
    h1st pmfp oraclize \
    My1stFaultPredTeacher <...teacher-model-version...> \
    \
    --input-cat-cols compressor1 compressor2 compressor3 \
    --input-num-cols high_pressure low_pressure \
    \
    --train-date-range 2016-09-01 2020-12-31 \
    --tune-date-range 2021-01-01 2021-12-31
"""


from typing import List, Tuple   # Py3.9+: use built-ins/collections.abc

import click

from h1st.contrib.pmfp.models import BaseFaultPredTeacher, FaultPredOracleModeler   # noqa: E501
from h1st.contrib.pmfp.models.oracle.student.timeseries_dl import N_MINUTES_PER_DAY   # noqa: E501

import h1st.utils.debug
from h1st.utils.path import add_cwd_to_py_path


@click.command(name='oraclize-fault-pred-teacher',
               cls=click.Command,

               # Command kwargs
               context_settings=None,
               # callback=None,
               # params=None,
               help='Oraclize a Fault-Prediction Knowledge ("Teacher") model >>>',   # noqa: E501
               epilog='^^^ Oraclize a Fault-Prediction Knowledge ("Teacher") model',  # noqa: E501
               short_help='Oraclize a Fault-Prediction Knowledge ("Teacher") model',  # noqa: E501
               options_metavar='[OPTIONS]',
               add_help_option=True,
               no_args_is_help=True,
               hidden=False,
               deprecated=False)
@click.argument('teacher_class_name',
                type=str,
                required=True,
                default=None,
                callback=None,
                nargs=None,
                # multiple=False,
                metavar='TEACHER_CLASS_NAME',
                expose_value=True,
                is_eager=False,
                envvar=None,
                # shell_complete=None,
                )
@click.argument('teacher_version',
                type=str,
                required=True,
                default=None,
                callback=None,
                nargs=None,
                # multiple=False,
                metavar='TEACHER_VERSION',
                expose_value=True,
                is_eager=False,
                envvar=None,
                # shell_complete=None,
                )
@click.option('--input-cat-cols',
              show_default=True,
              prompt=False,
              confirmation_prompt=False,
              # prompt_required=True,
              hide_input=False,
              is_flag=False,
              flag_value=None,
              multiple=False,
              count=False,
              allow_from_autoenv=True,
              help='Comma-separated Input Categorical Columns',
              hidden=False,
              show_choices=True,
              show_envvar=False,

              type=str,
              required=False,
              default='',
              callback=None,
              nargs=None,
              # multiple=False,
              metavar='INPUT_CAT_COL,INPUT_CAT_COL,...',
              expose_value=True,
              is_eager=False,
              envvar=None,
              # shell_complete=None,
              )
@click.option('--input-num-cols',
              show_default=True,
              prompt=False,
              confirmation_prompt=False,
              # prompt_required=True,
              hide_input=False,
              is_flag=False,
              flag_value=None,
              multiple=False,
              count=False,
              allow_from_autoenv=True,
              help='Comma-separated Input Numerical Columns',
              hidden=False,
              show_choices=True,
              show_envvar=False,

              type=str,
              required=False,
              default='',
              callback=None,
              nargs=None,
              # multiple=False,
              metavar='INPUT_NUM_COL,INPUT_NUM_COL,...',
              expose_value=True,
              is_eager=False,
              envvar=None,
              # shell_complete=None,
              )
@click.option('--input-subsampling-factor',
              show_default=True,
              prompt=False,
              confirmation_prompt=False,
              # prompt_required=True,
              hide_input=False,
              is_flag=False,
              flag_value=None,
              multiple=False,
              count=False,
              allow_from_autoenv=True,
              help='Input Sub-Sampling Factor (positive int)',
              hidden=False,
              show_choices=True,
              show_envvar=False,

              type=int,
              required=False,
              default=1,
              callback=None,
              nargs=None,
              # multiple=False,
              metavar='INPUT_SUBSAMPLING_FACTOR',
              expose_value=True,
              is_eager=False,
              envvar=None,
              # shell_complete=None,
              )
@click.option('--input-n-rows-per-day',
              show_default=True,
              prompt=False,
              confirmation_prompt=False,
              # prompt_required=True,
              hide_input=False,
              is_flag=False,
              flag_value=None,
              multiple=False,
              count=False,
              allow_from_autoenv=True,
              help='Input No. of Rows per Day (positive int)',
              hidden=False,
              show_choices=True,
              show_envvar=False,

              type=int,
              required=False,
              default=N_MINUTES_PER_DAY,
              callback=None,
              nargs=None,
              # multiple=False,
              metavar='INPUT_N_ROWS_PER_DAY',
              expose_value=True,
              is_eager=False,
              envvar=None,
              # shell_complete=None,
              )
@click.option('--train-date-range',
              show_default=False,
              prompt=False,
              confirmation_prompt=False,
              # prompt_required=True,
              hide_input=False,
              is_flag=False,
              flag_value=None,
              multiple=False,
              count=False,
              allow_from_autoenv=True,
              help='Training Data Date Range',
              hidden=False,
              show_choices=True,
              show_envvar=False,

              type=str,
              required=True,
              default=None,
              callback=None,
              nargs=2,
              # multiple=False,
              metavar='TRAIN_FROM_DATE TRAIN_TO_DATE',
              expose_value=True,
              is_eager=False,
              envvar=None,
              # shell_complete=None,
              )
@click.option('--tune-date-range',
              show_default=False,
              prompt=False,
              confirmation_prompt=False,
              # prompt_required=True,
              hide_input=False,
              is_flag=False,
              flag_value=None,
              multiple=False,
              count=False,
              allow_from_autoenv=True,
              help='Decision-Threshold-Tuning Data Date Range',
              hidden=False,
              show_choices=True,
              show_envvar=False,

              type=str,
              required=True,
              default=None,
              callback=None,
              nargs=2,
              # multiple=False,
              metavar='TUNE_FROM_DATE TUNE_TO_DATE',
              expose_value=True,
              is_eager=False,
              envvar=None,
              # shell_complete=None,
              )
@click.option('--debug',
              show_default=True,
              prompt=False,
              confirmation_prompt=False,
              # prompt_required=True,
              hide_input=False,
              is_flag=True,
              flag_value=True,
              multiple=False,
              count=False,
              allow_from_autoenv=True,
              help='Run in DEBUG mode',
              hidden=False,
              show_choices=True,
              show_envvar=False,

              type=bool,
              required=False,
              default=False,
              callback=None,
              nargs=None,
              # multiple=False,
              metavar='DEBUG',
              expose_value=True,
              is_eager=False,
              envvar=None,
              # shell_complete=None,
              )
def oraclize_fault_pred_teacher(teacher_class_name: str, teacher_version: str,
                                input_cat_cols: str, input_num_cols: str,
                                input_subsampling_factor: int,
                                input_n_rows_per_day: int,
                                train_date_range: Tuple[str, str],
                                tune_date_range: Tuple[str, str],
                                debug: bool = False):
    """Oraclize a Fault-Prediction Knowledge ("Teacher") model."""
    assert input_cat_cols or input_num_cols
    input_cat_cols: List[str] = input_cat_cols.split(sep=',', maxsplit=-1)
    input_num_cols: List[str] = input_num_cols.split(sep=',', maxsplit=-1)

    if debug:
        h1st.utils.debug.ON = True

    # load Teacher model
    add_cwd_to_py_path()
    import ai.models   # pylint: disable=import-error,import-outside-toplevel

    teacher: BaseFaultPredTeacher = (getattr(ai.models, teacher_class_name)
                                     .load(version=teacher_version))

    # oraclize Teacher model
    FaultPredOracleModeler(
        teacher=teacher,

        student_input_cat_cols=input_cat_cols,
        student_input_num_cols=input_num_cols,
        student_input_subsampling_factor=input_subsampling_factor,
        student_input_n_rows_per_day=input_n_rows_per_day,

        student_train_date_range=train_date_range,
        student_tuning_date_range=tune_date_range,

    ).build_model()
