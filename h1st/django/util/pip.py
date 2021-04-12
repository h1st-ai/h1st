from pip._internal.operations.freeze import freeze


def get_python_dependencies():
    d = {}

    for deps_and_vers in freeze():
        ls = deps_and_vers.split('==')

        if len(ls) == 2:
            d[ls[0]] = ls[1]

        else:
            assert len(ls) == 1, f'*** {ls} ***'
            d[ls[0]] = None

    return d
