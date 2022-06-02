"""AWS S3 utilities."""


from logging import getLogger, Logger, INFO
import os
import time
from typing import Optional

import botocore
import boto3

from h1st.utils.fs import PathType
from h1st.utils.iter import to_iterable
from h1st.utils.log import STDOUT_HANDLER


__all__ = 'client', 'cp', 'mv', 'rm', 'sync'


_LOGGER: Logger = getLogger(name=__name__)
_LOGGER.setLevel(level=INFO)
_LOGGER.addHandler(hdlr=STDOUT_HANDLER)


_CLIENT = None


def client(region: Optional[str] = None,
           access_key: Optional[str] = None, secret_key: Optional[str] = None):
    """Get Boto3 S3 Client."""
    global _CLIENT   # pylint: disable=global-statement

    if _CLIENT is None:
        _CLIENT = boto3.client(service_name='s3',
                               region_name=region,
                               api_version=None,
                               use_ssl=True,
                               verify=None,
                               endpoint_url=None,
                               aws_access_key_id=access_key,
                               aws_secret_access_key=secret_key,
                               aws_session_token=None,
                               config=botocore.client.Config(connect_timeout=9,
                                                             read_timeout=9))

    return _CLIENT


def cp(from_path: PathType, to_path: PathType,
       *, is_dir: bool = True,
       quiet: bool = True, verbose: bool = True):
    # pylint: disable=invalid-name,too-many-arguments
    """Copy a directory or a file between S3 paths or between S3 and local."""
    s3_command: str = (f'aws s3 cp {from_path} {to_path}' +
                       (' --recursive' if is_dir else '') +
                       (' --quiet' if quiet else ''))

    if verbose:
        _LOGGER.info(msg=(msg := f'Copying "{from_path}" to "{to_path}"...'))
        _LOGGER.debug(msg=f'Running: {s3_command}...')
        tic: float = time.time()

    os.system(command=s3_command)

    if verbose:
        toc: float = time.time()
        _LOGGER.info(msg=f'{msg} done!   <{toc - tic:,.1f} s>')


def mv(from_path: PathType, to_path: PathType,
       *, is_dir: bool = True,
       quiet: bool = True, verbose: bool = True):
    # pylint: disable=invalid-name,too-many-arguments
    """Move a directory or a file between S3 paths or between S3 and local."""
    s3_command: str = (f'aws s3 mv {from_path} {to_path}' +
                       (' --recursive' if is_dir else '') +
                       (' --quiet' if quiet else ''))

    if verbose:
        _LOGGER.info(msg=(msg := f'Moving "{from_path}" to "{to_path}"...'))
        _LOGGER.debug(msg=f'Running: {s3_command}...')
        tic: float = time.time()

    os.system(command=s3_command)

    if verbose:
        toc: float = time.time()
        _LOGGER.info(msg=f'{msg} done!   <{toc - tic:,.1f} s>')


def rm(path: PathType,
       *, is_dir: bool = True, globs: Optional[str] = None,
       quiet: bool = True, verbose: bool = True):
    # pylint: disable=invalid-name,too-many-arguments
    """Remove a directory, a file, or glob-pattern-matched items from S3."""
    s3_command: str = (f'aws s3 rm {path}' +
                       ((' --recursive' +
                         ((' --exclude "*" ' +
                           ' '.join(f'--include "{glob}"'
                                    for glob in to_iterable(globs)))
                          if globs
                          else ''))
                        if is_dir
                        else '') +
                       (' --quiet' if quiet else ''))

    if verbose:
        _LOGGER.info(msg=(msg := ('Deleting ' +
                                  ((f'Globs "{globs}" @ '
                                    if globs
                                    else 'Directory ')
                                   if is_dir
                                   else '') +
                                  f'"{path}"...')))
        _LOGGER.debug(msg=f'Running: {s3_command}...')
        tic: float = time.time()

    os.system(command=s3_command)

    if verbose:
        toc: float = time.time()
        _LOGGER.info(msg=f'{msg} done!   <{toc - tic:,.1f} s>')


def sync(from_dir_path: PathType, to_dir_path: PathType,
         *, delete: bool = True,
         quiet: bool = True, verbose=True):
    # pylint: disable=too-many-arguments
    """Sync a directory between S3 paths or between S3 and local."""
    s3_command: str = (f'aws s3 sync {from_dir_path} {to_dir_path}' +
                       (' --delete' if delete else '') +
                       (' --quiet' if quiet else ''))

    if verbose:
        _LOGGER.info(msg=(msg := f'Syncing "{from_dir_path}" to "{to_dir_path}"...'))   # noqa: E501
        _LOGGER.debug(msg=f'Running: {s3_command}...')
        tic = time.time()

    os.system(command=s3_command)

    if verbose:
        toc = time.time()
        _LOGGER.info(msg=f'{msg} done!   <{toc - tic:,.1f} s>')
