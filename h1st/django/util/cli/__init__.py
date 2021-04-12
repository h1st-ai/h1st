import os
from pathlib import Path
import shutil
from typing import Optional

from ..config import _H1ST_DJANGO_CONFIG_FILE_NAME, parse_config_file
from ..git import _GIT_HASH_FILE_NAME, get_git_repo_head_commit_hash


_H1ST_DJANGO_UTIL_CLI_STANDARD_FILES_DIR_PATH = \
    Path(__file__).parent / '_standard_files'

_ASGI_PY_FILE_NAME = 'asgi.py'
_ASGI_PY_FILE_SRC_PATH = \
    _H1ST_DJANGO_UTIL_CLI_STANDARD_FILES_DIR_PATH / _ASGI_PY_FILE_NAME

_WSGI_PY_FILE_NAME = 'wsgi.py'
_WSGI_PY_FILE_SRC_PATH = \
    _H1ST_DJANGO_UTIL_CLI_STANDARD_FILES_DIR_PATH / _WSGI_PY_FILE_NAME

_PROCFILE_NAME = 'Procfile'


def run_command_with_config_file(
        command: str,
        h1st_django_config_file_path: str,
        copy_standard_files: bool = False,
        asgi: Optional[str] = None):
    h1st_django_config_file_path = \
        Path(h1st_django_config_file_path).expanduser()

    # verify config file is valid
    config = parse_config_file(path=h1st_django_config_file_path)

    if copy_standard_files:
        assert not os.path.exists(path=_H1ST_DJANGO_CONFIG_FILE_NAME)
        shutil.copyfile(
            src=h1st_django_config_file_path,
            dst=_H1ST_DJANGO_CONFIG_FILE_NAME)

        if asgi:
            assert not os.path.exists(path=_ASGI_PY_FILE_NAME)
            shutil.copyfile(
                src=_ASGI_PY_FILE_SRC_PATH,
                dst=_ASGI_PY_FILE_NAME)
            assert not os.path.exists(path=_PROCFILE_NAME)
            shutil.copyfile(
                src=_H1ST_DJANGO_UTIL_CLI_STANDARD_FILES_DIR_PATH /
                    f'{_PROCFILE_NAME}.{asgi.capitalize()}',
                dst=_PROCFILE_NAME)
        else:
            assert not os.path.exists(path=_WSGI_PY_FILE_NAME)
            shutil.copyfile(
                src=_WSGI_PY_FILE_SRC_PATH,
                dst=_WSGI_PY_FILE_NAME)

        assert not os.path.exists(path=_GIT_HASH_FILE_NAME)
        git_hash = get_git_repo_head_commit_hash()
        if git_hash:
            with open(_GIT_HASH_FILE_NAME, 'w') as f:
                f.write(git_hash)

    aws_config = config.get('aws')
    if aws_config:
        key = aws_config.get('key')
        secret = aws_config.get('secret')
        if key and secret:
            os.environ.setdefault('AWS_ACCESS_KEY_ID', key)
            os.environ.setdefault('AWS_SECRET_ACCESS_KEY', secret)

    print(f'Running Command: {command}...')
    os.system(
        (''
         if copy_standard_files
         else f'H1ST_DJANGO_CONFIG_FILE_PATH={h1st_django_config_file_path} ')
        + command)

    if copy_standard_files:
        os.remove(_H1ST_DJANGO_CONFIG_FILE_NAME)
        assert not os.path.exists(path=_H1ST_DJANGO_CONFIG_FILE_NAME)

        if asgi:
            os.remove(_ASGI_PY_FILE_NAME)
            assert not os.path.exists(path=_ASGI_PY_FILE_NAME)
            os.remove(_PROCFILE_NAME)
            assert not os.path.exists(path=_PROCFILE_NAME)
        else:
            os.remove(_WSGI_PY_FILE_NAME)
            assert not os.path.exists(path=_WSGI_PY_FILE_NAME)

        if git_hash:
            os.remove(_GIT_HASH_FILE_NAME)
            assert not os.path.exists(path=_GIT_HASH_FILE_NAME)
