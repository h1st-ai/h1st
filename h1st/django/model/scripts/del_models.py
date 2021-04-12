from ..models import H1stModel


def run(*uuids):
    models_to_delete = H1stModel.objects.filter(uuid__in=uuids)
    print(f'*** DELETING: {models_to_delete}... ', end='')
    models_to_delete.delete()
    print('DONE! ***')
