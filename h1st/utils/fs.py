"""Local File System & HDFS utilities."""


from logging import getLogger, Logger, DEBUG
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Union

from pyarrow.hdfs import HadoopFileSystem

from h1st.utils.log import STDOUT_HANDLER


__all__ = (
    'PathType',
    '_HADOOP_HOME_ENV_VAR_NAME', '_HADOOP_HOME',
    '_HADOOP_CONF_DIR_ENV_VAR_NAME',
    '_ON_LINUX_CLUSTER',
    'HDFS_CLIENT',
    'exist',
    'mkdir',
    'rm', 'empty',
    'cp', 'mv',
    'get', 'put',
)


_LOGGER: Logger = getLogger(name=__name__)
_LOGGER.setLevel(level=DEBUG)
_LOGGER.addHandler(hdlr=STDOUT_HANDLER)


PathType = Union[str, Path]


# Hadoop configuration directory
_HADOOP_HOME_ENV_VAR_NAME: str = 'HADOOP_HOME'
_HADOOP_HOME: PathType = os.environ.get(_HADOOP_HOME_ENV_VAR_NAME)


def _hdfs_cmd(hadoop_home: PathType = _HADOOP_HOME) -> str:
    if hadoop_home:
        cmd: str = f'{hadoop_home}/bin/hdfs'

        if Path(cmd).resolve(strict=True).is_file():
            return cmd

        return 'hdfs'

    return 'hdfs'


_HADOOP_CONF_DIR_ENV_VAR_NAME: str = 'HADOOP_CONF_DIR'


# check if running on Linux cluster or local Mac
_ON_LINUX_CLUSTER: bool = sys.platform.startswith('linux')


# detect & set up HDFS client
if _HADOOP_HOME:
    os.environ['ARROW_LIBHDFS_DIR'] = \
        str(Path(_HADOOP_HOME).resolve(strict=True) / 'lib' / 'native')

    try:
        HDFS_CLIENT = HadoopFileSystem()

        try:
            _LOGGER.debug(msg=(msg := 'Testing HDFS...'))

            if HDFS_CLIENT.isdir(path='/'):
                _ON_LINUX_CLUSTER_WITH_HDFS: bool = True
                _LOGGER.debug(msg=f'{msg} done!')

            else:
                _ON_LINUX_CLUSTER_WITH_HDFS: bool = False
                _LOGGER.debug(msg=f'{msg} UNAVAILABLE')

        except Exception:   # pylint: disable=broad-except
            HDFS_CLIENT = None
            _ON_LINUX_CLUSTER_WITH_HDFS: bool = False
            _LOGGER.debug(msg=f'{msg} UNAVAILABLE')

    except Exception:   # pylint: disable=broad-except
        HDFS_CLIENT = None
        _ON_LINUX_CLUSTER_WITH_HDFS: bool = False
        _LOGGER.debug(msg='*** HDFS UNAVAILABLE ***')

else:
    HDFS_CLIENT = None
    _ON_LINUX_CLUSTER_WITH_HDFS: bool = False


def _exec(cmd: str, must_succeed: bool = False):
    with subprocess.Popen(cmd,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,
                          shell=True) as proc:
        out, err = proc.communicate()

        if must_succeed and proc.returncode:
            raise RuntimeError(f'*** COMMAND ERROR: {cmd} ***\n{out}\n{err}\n')


def command_prefix(hdfs: bool = True, hadoop_home: PathType = '/opt/hadoop') -> str:   # noqa: E501
    """Get command prefix."""
    return f'{_hdfs_cmd(hadoop_home=hadoop_home)} dfs -' if hdfs else ''


def exist(path: PathType, *, hdfs: bool = False, is_dir: bool = False) -> bool:
    """Check whether path exists."""
    if hdfs and _ON_LINUX_CLUSTER_WITH_HDFS:
        return (HDFS_CLIENT.isdir(path=path)
                if is_dir
                else HDFS_CLIENT.isfile(path=path))

    path: Path = Path(path).resolve(strict=False)
    return (path.is_dir()
            if is_dir
            else (path.is_file() or path.is_symlink()))


def mkdir(dir_path: PathType,
          *, hdfs: bool = True, hadoop_home: PathType = '/opt/hadoop'):
    """Make directory."""
    cmd_prefix: str = command_prefix(hdfs=hdfs, hadoop_home=hadoop_home)

    command: str = (f'{cmd_prefix}mkdir -p "{dir_path}"' +
                    (' -m 0777' if _ON_LINUX_CLUSTER and (not hdfs) else ''))

    _ = os.system(command=command)
    assert _ <= 0, OSError(f'*** FAILED: {command} (EXIT CODE: {_}) ***')


def rm(path: PathType, *, hdfs: bool = True, is_dir: bool = True,
       hadoop_home: PathType = '/opt/hadoop'):
    # pylint: disable=invalid-name
    """Remove directory or file."""
    if not _ON_LINUX_CLUSTER_WITH_HDFS:
        hdfs: bool = False

    if hdfs:
        os.system(
            command=f'{command_prefix(hdfs=True, hadoop_home=hadoop_home)}rm' +
                    (' -r' if is_dir else '') +
                    f' -skipTrash "{path}"')

    else:
        path: Path = Path(path).resolve(strict=False)

        if is_dir and path.is_dir():
            try:
                shutil.rmtree(path=path, ignore_errors=False, onerror=None)

            except Exception:   # pylint: disable=broad-except
                os.system(command=f'rm -f "{path}"')

            assert not path.is_dir(), \
                OSError(f'*** CANNOT REMOVE LOCAL DIR "{path}" ***')

        elif path.is_file() or path.is_symlink():
            os.remove(path=path)

            assert not (path.is_file() or path.is_symlink()), \
                OSError(f'*** CANNOT REMOVE LOCAL FILE/SYMLINK "{path}" ***')


def empty(dir_path: PathType,
          *, hdfs: bool = True, hadoop_home: PathType = '/opt/hadoop'):
    """Empty directory."""
    if exist(path=dir_path, hdfs=hdfs, is_dir=True):
        rm(path=dir_path, hdfs=hdfs, is_dir=True, hadoop_home=hadoop_home)

    mkdir(dir_path=dir_path, hdfs=hdfs, hadoop_home=hadoop_home)


def cp(from_path: PathType, to_path: PathType,
       *, hdfs: bool = True, is_dir: bool = True,
       hadoop_home: PathType = '/opt/hadoop'):
    # pylint: disable=invalid-name
    """Copy directory or file."""
    rm(path=to_path, hdfs=hdfs, is_dir=is_dir, hadoop_home=hadoop_home)

    to_path = Path(to_path).resolve(strict=False)
    mkdir(dir_path=to_path.parent, hdfs=hdfs, hadoop_home=hadoop_home)

    if hdfs:
        os.system(
            command=(f'{command_prefix(hdfs=True, hadoop_home=hadoop_home)}cp '
                     f'"{from_path}" "{to_path}"'))

    elif is_dir:
        shutil.copytree(src=from_path,
                        dst=to_path,
                        symlinks=False,
                        ignore=None,
                        ignore_dangling_symlinks=False,
                        dirs_exist_ok=False)

    else:
        shutil.copyfile(src=from_path, dst=to_path, follow_symlinks=True)


def mv(from_path: PathType, to_path: PathType,
       *, hdfs: bool = True, is_dir: bool = True,
       hadoop_home: PathType = '/opt/hadoop'):
    # pylint: disable=invalid-name
    """Move directory or file."""
    rm(path=to_path, hdfs=hdfs, is_dir=is_dir, hadoop_home=hadoop_home)

    to_path = Path(to_path).resolve(strict=False)
    mkdir(dir_path=to_path.parent, hdfs=hdfs, hadoop_home=hadoop_home)

    if hdfs:
        os.system(
            command=(f'{command_prefix(hdfs=hdfs, hadoop_home=hadoop_home)}mv '
                     f'"{from_path}" "{to_path}"'))

    else:
        try:
            shutil.move(src=from_path, dst=to_path)

        except Exception:   # pylint: disable=broad-except
            os.system(command=f'mv "{from_path}" "{to_path}"')


def get(from_hdfs: PathType, to_local: PathType,
        *, is_dir: bool = False, overwrite: bool = True, _mv: bool = False,
        hadoop_home: PathType = '/opt/hadoop',
        must_succeed: bool = False,
        _on_linux_cluster_with_hdfs: bool = _ON_LINUX_CLUSTER_WITH_HDFS):
    """Get directory or file from HDFS to local."""
    if _on_linux_cluster_with_hdfs:
        if overwrite:
            rm(path=to_local, hdfs=False, is_dir=is_dir)

        to_local = Path(to_local).resolve(strict=False)

        if overwrite or \
                (is_dir and (not to_local.is_dir())) or \
                ((not is_dir) and (not to_local.is_file())):
            mkdir(dir_path=to_local.parent, hdfs=False)

            _exec(cmd=f'{_hdfs_cmd(hadoop_home=hadoop_home)} dfs -get '
                      f'"{from_hdfs}" "{to_local}"')

            if _mv:
                rm(path=from_hdfs, hdfs=True, is_dir=is_dir, hadoop_home=hadoop_home)   # noqa: E501

    elif from_hdfs != to_local:
        if _mv:
            mv(from_path=from_hdfs, to_path=to_local, hdfs=False, is_dir=is_dir)   # noqa: E501

        else:
            cp(from_path=from_hdfs, to_path=to_local, hdfs=False, is_dir=is_dir)   # noqa: E501

    if must_succeed:
        if isinstance(to_local, str):
            to_local = Path(to_local).resolve(strict=False)

        assert to_local.is_dir() if is_dir else to_local.is_file(), \
            OSError(f'*** FS.GET({from_hdfs} -> {to_local}) FAILED! ***')


def put(from_local: PathType, to_hdfs: PathType,
        *, is_dir: bool = True, _mv: bool = True,
        hadoop_home: PathType = '/opt/hadoop'):
    """Put directory or file from local to HDFS."""
    if _ON_LINUX_CLUSTER_WITH_HDFS:
        rm(path=to_hdfs, hdfs=True, is_dir=is_dir, hadoop_home=hadoop_home)

        to_hdfs = Path(to_hdfs).resolve(strict=False)
        mkdir(dir_path=to_hdfs.parent, hdfs=True, hadoop_home=hadoop_home)

        os.system(command=f'{_hdfs_cmd(hadoop_home=hadoop_home)} dfs -put '
                          f'"{from_local}" "{to_hdfs}"')

        if _mv:
            rm(path=from_local, hdfs=False, is_dir=is_dir)

    elif from_local != to_hdfs:
        if _mv:
            mv(from_path=from_local, to_path=to_hdfs, hdfs=False, is_dir=is_dir)   # noqa: E501

        else:
            cp(from_path=from_local, to_path=to_hdfs, hdfs=False, is_dir=is_dir)   # noqa: E501
