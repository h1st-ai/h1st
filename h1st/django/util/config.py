from django.conf import settings
from django.core.wsgi import get_wsgi_application
from django.core.asgi import get_asgi_application

import os
from pathlib import Path
from ruamel import yaml
import sys


_H1ST_DJANGO_CONFIG_FILE_NAME = '.config.yml'


def parse_config_file(path=None):
    if path is None:
        path = os.environ.get(
                'H1ST_DJANGO_CONFIG_FILE_PATH',
                _H1ST_DJANGO_CONFIG_FILE_NAME)

    if os.path.isfile(path):
        # parse whole YAML config file
        config = yaml.safe_load(stream=open(path))

        # read and adjust DB config section
        db_config = config.get('db')
        assert db_config, f'*** "db" KEY NOT FOUND IN {config} ***'

        db_engine = db_config.get('engine')
        assert db_engine, f'*** "engine" KEY NOT FOUND IN {db_config} ***'
        assert db_engine in ('postgresql', 'mysql', 'sqlite3'), \
            ValueError(f'*** "{db_engine}" DATABASE ENGINE NOT SUPPORTED ***')

        db_name = db_config.get('name')
        assert db_name, f'*** "name" KEY NOT FOUND IN {db_config} ***'

        db_host = db_config.get('host')
        db_user = db_config.get('user')
        db_password = db_config.get('password')
        if db_engine != 'sqlite3':
            assert db_host, f'*** HOST NOT FOUND IN {db_config} ***'
            assert db_user, f'*** USER NOT FOUND IN {db_config} ***'
            assert db_password, f'*** PASSWORD NOT FOUND IN {db_config} ***'

        config['db'] = dict(ENGINE=f'django.db.backends.{db_engine}',
                            NAME=db_name,
                            HOST=db_host,
                            PORT=(5432
                                  if db_engine == 'postgresql'
                                  else (3306
                                        if db_engine == 'mysql'
                                        else None)),
                            USER=db_user,
                            PASSWORD=db_password)

        return config

    else:
        # return blank config per template
        return yaml.safe_load(
                stream=open(Path(__file__).parent /
                            'cli' /
                            '_standard_files' /
                            f'{_H1ST_DJANGO_CONFIG_FILE_NAME}.template'))


def config_app(
        app_dir_path: str,
        config_file_path: str,
        asgi=False):
    sys.path.append(
        str(Path(app_dir_path).resolve())   # must be string, absolute path
    )
    import settings as _settings

    config = parse_config_file(path=config_file_path)
    _settings.DATABASES['default'] = config['db']

    os.chdir(path=app_dir_path)

    # ref: https://code.djangoproject.com/ticket/31056
    os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

    settings.configure(
        **{SETTING_KEY: setting_value
           for SETTING_KEY, setting_value in _settings.__dict__.items()
           if SETTING_KEY.isupper()})

    if asgi:
        get_asgi_application()
    else:
        get_wsgi_application()
