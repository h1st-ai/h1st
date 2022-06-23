"""H1st Predictive Maintenance / Fault Prediction ("PMFP") CLI."""


import click

from .oracle import (oraclize_fault_pred_teacher,
                     predict_faults,
                     tune_fault_pred_student_decision_threshold)


__all__ = ('h1st_pmfp_cli',)


@click.group(name='pmfp',
             cls=click.Group,
             commands={
                'oraclize': oraclize_fault_pred_teacher,
                'predict-faults': predict_faults,
                'tune-decision-threshold': tune_fault_pred_student_decision_threshold,  # noqa: E501
             },

             # Command kwargs
             context_settings=None,
             # callback=None,
             # params=None,
             help='H1st Predictive Maintenance / Fault Prediction ("PMFP") CLI >>>',   # noqa: E501
             epilog='^^^ H1st Predictive Maintenance / Fault Prediction ("PMFP") CLI',  # noqa: E501
             short_help='H1st Predictive Maintenance / Fault Prediction ("PMFP") CLI',  # noqa: E501
             options_metavar='[OPTIONS]',
             add_help_option=True,
             no_args_is_help=True,
             hidden=False,
             deprecated=False,

             # Group/MultiCommand kwargs
             invoke_without_command=False,
             subcommand_metavar='H1ST_PMFP_SUB_COMMAND',
             chain=False,
             result_callback=None)
def h1st_pmfp_cli():
    """H1st Predictive Maintenance / Fault Prediction ("PMFP") CLI."""
