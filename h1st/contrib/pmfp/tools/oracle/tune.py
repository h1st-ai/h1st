"""Tune a Knowledge Generalizer ("Student") model's decision threshold.

Example:
AWS_ACCESS_KEY_ID=<...aws-access-key-id...> \
AWS_SECRET_ACCESS_KEY=<...aws-secret-access-key...> \
    h1st pmfp tune-decision-threshold \
    <...student-model-version...> \
    2016-09-01 2022-02-22
"""


from typing import Tuple   # Python 3.9+: use built-ins/collections.abc

import click

from h1st.contrib.pmfp.models import TimeSeriesDLFaultPredStudent

import h1st.utils.debug


@click.command(name='tune-fault-pred-student-decision-threshold',
               cls=click.Command,

               # Command kwargs
               context_settings=None,
               # callback=None,
               # params=None,
               help="Tune a Student model's decision threshold >>>",   # noqa: E501
               epilog="^^^ Tune a Student model's decision threshold",  # noqa: E501
               short_help="Tune a Student model's decision threshold",  # noqa: E501
               options_metavar='[OPTIONS]',
               add_help_option=True,
               no_args_is_help=True,
               hidden=False,
               deprecated=False)
@click.argument('student_version',
                type=str,
                required=True,
                default=None,
                callback=None,
                nargs=None,
                # multiple=False,
                metavar='STUDENT_VERSION',
                expose_value=True,
                is_eager=False,
                envvar=None,
                # shell_complete=None,
                )
@click.argument('date_range',
                type=str,
                required=True,
                default=None,
                callback=None,
                nargs=2,
                # multiple=False,
                metavar='FROM_DATE TO_DATE',
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
def tune_fault_pred_student_decision_threshold(student_version: str,
                                               date_range: Tuple[str, str],
                                               debug: bool = False):
    """Tune a Knowledge Generalizer ("Student") model's decision threshold."""
    if debug:
        h1st.utils.debug.ON = True

    # load Student model
    student: TimeSeriesDLFaultPredStudent = \
        TimeSeriesDLFaultPredStudent.load(version=student_version)

    # tune Student's decision threshold
    student.tune_decision_threshold(tuning_date_range=date_range)
