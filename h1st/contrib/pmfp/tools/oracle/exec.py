"""Batch-predict equipment faults.

Example:
AWS_ACCESS_KEY_ID=<...aws-access-key-id...> \
AWS_SECRET_ACCESS_KEY=<...aws-secret-access-key...> \
    h1st pmfp predict-faults \
    <...model-class-name...> \
    <...model-version...> \
    --from-date 2016-09-01 --to-date 2022-02-22
"""

from pathlib import Path
from pprint import pprint
from typing import Optional

import click
from pandas import Series

from h1st.contrib.pmfp.models import BaseFaultPredictor, H1ST_BATCH_OUTPUT_DIR_PATH   # noqa: E501

import h1st.utils.debug
from h1st.utils.path import add_cwd_to_py_path


@click.command(name='predict-faults',
               cls=click.Command,

               # Command kwargs
               context_settings=None,
               # callback=None,
               # params=None,
               help='Batch-predict equipment faults >>>',   # noqa: E501
               epilog='^^^ Batch-predict equipment faults',  # noqa: E501
               short_help='Batch-predict equipment faults',  # noqa: E501
               options_metavar='[OPTIONS]',
               add_help_option=True,
               no_args_is_help=True,
               hidden=False,
               deprecated=False)
@click.argument('model_class_name',
                type=str,
                required=True,
                default=None,
                callback=None,
                nargs=None,
                # multiple=False,
                metavar='MODEL_CLASS_NAME',
                expose_value=True,
                is_eager=False,
                envvar=None,
                # shell_complete=None,
                )
@click.argument('model_version',
                type=str,
                required=True,
                default=None,
                callback=None,
                nargs=None,
                # multiple=False,
                metavar='MODEL_VERSION',
                expose_value=True,
                is_eager=False,
                envvar=None,
                # shell_complete=None,
                )
@click.argument('date',
                type=str,
                required=True,
                default=None,
                callback=None,
                nargs=None,
                # multiple=False,
                metavar='DATE',
                expose_value=True,
                is_eager=False,
                envvar=None,
                # shell_complete=None,
                )
@click.option('--to-date',
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
              help='To Date (YYYY-MM-DD)',
              hidden=False,
              show_choices=True,
              show_envvar=False,

              type=str,
              required=False,
              default=None,
              callback=None,
              nargs=None,
              # multiple=False,
              metavar='TO_DATE',
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
def predict_faults(
        model_class_name: str, model_version: str,
        date: str, to_date: Optional[str] = None,
        debug: bool = False):
    """Batch-predict equipment faults."""
    if debug:
        h1st.utils.debug.ON = True

    # load model
    add_cwd_to_py_path()
    import ai.models   # pylint: disable=import-error,import-outside-toplevel

    model: BaseFaultPredictor = (getattr(ai.models, model_class_name)
                                 .load(version=model_version))

    # predict
    results: Series = model.batch_process(date=date, to_date=to_date,
                                          return_json=False)

    # filter for positive predictions
    fault_preds: Series = results.loc[(results.map(sum) > 0)
                                      if isinstance(results.iloc[0], tuple)
                                      else results]

    # print
    pprint(fault_preds.to_dict())

    # save
    Path(output_path := (f'{H1ST_BATCH_OUTPUT_DIR_PATH}/'
                         f'{model_class_name}/{model_version}/'
                         f'{date}-to-{to_date}.csv')
         ).parent.mkdir(parents=True, exist_ok=True)
    fault_preds.to_csv(output_path, header=True, index=True)
    print(f'\n@ {output_path}')

    # summarize
    print(f'\n{(n_faults := len(fault_preds)):,} Predicted Daily Faults '
          f'({100 * n_faults / (n := len(results)):.3f}% of {n:,})')
