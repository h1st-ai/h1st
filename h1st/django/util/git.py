from git.exc import InvalidGitRepositoryError
from git.repo.base import Repo
import os


_GIT_HASH_FILE_NAME = '.git-hash'


def get_git_repo_head_commit_hash(path=None):
    try:
        repo = Repo(path=path,
                    search_parent_directories=True,
                    expand_vars=True)

    except InvalidGitRepositoryError:
        if os.path.isfile(_GIT_HASH_FILE_NAME):
            with open(_GIT_HASH_FILE_NAME) as f:
                return f.read()

        else:
            return

    return repo.head.commit.hexsha
