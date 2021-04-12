PGSQL_IDENTIFIER_MAX_LEN = 63


def dir_path_with_slash(path: str) -> str:
    return path \
        if path.endswith('/') \
      else f'{path}/'
