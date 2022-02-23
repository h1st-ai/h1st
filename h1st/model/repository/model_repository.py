import os
import tarfile
import tempfile
import logging
import importlib
from distutils import dir_util

import yaml
import ulid
from h1st.model.modelable import Modelable

from h1st.model.repository.storage.s3 import S3Storage
from h1st.model.repository.storage.local import LocalStorage
from h1st.model.repository.model_serdes import ModelSerDes

SEP = "::"
logger = logging.getLogger(__name__)


class ModelRepository:
    """
    Model repository allows user to persist and load model to different storage system.

    Model repository uses ``ModelSerDes`` to serialize a model into a temporary folder
    and then create a tar archive to store on storage. For loading, the repo retrieve
    the tar archive from the storage and then extract to temporary folder for restoring
    the model object.
    """

    _NAMESPACE = "_models"

    _DEFAULT_STORAGE = S3Storage

    _singleton = None

    def __init__(self, repository_path = None):
        if isinstance(repository_path, str):
            self._NAMESPACE = ""
            if  "s3://" in repository_path:
                repository_path = repository_path.replace("s3://", "").strip("/") + "/"
                bucket, prefix = repository_path.split("/", 1)
                storage = S3Storage(bucket, prefix.strip("/"))
            else:
                storage = LocalStorage(repository_path)

        self._storage = storage or ModelRepository._DEFAULT_STORAGE()
        self._serdes = ModelSerDes()

    def persist_model(self, model_object, version=None) -> str:
        """
        Save a model to the model repository

        :param model_object:
        :param version: version name, leave blank for autogeneration
        :return: model version
        :rypte: str
        """
        # assert isinstance(model, Model)
        # TODO: use version format: v_20200714-1203
        if not model_object:
            return None
        model_class = model_object.__class__
        version = version or str(ulid.new())

        try:
            # serialize the model_object to a temporary folder and then clean up later
            temp_dir, serdes_dir, tar_file = _make_temp_serdes_dir()

            self._serdes.serialize(model_object, serdes_dir)
            _tar_create(tar_file, serdes_dir)

            # copy serialized bytes from temp to permanent storage
            with open(tar_file, mode='rb') as f:
                self._storage.set_bytes(
                    self._get_key(model_object, version),
                    f.read(),
                )

                self._storage.set_obj(
                    self._get_key(model_object, 'latest'),
                    version,
                )

        finally:
            model_object.version = version
            # clean up temp
            dir_util.remove_tree(temp_dir)

        return model_object.version

    def load_model(self, model_class, version=None) -> Modelable:
        """
        Restore the model from the model repository

        :param model_class: class of model to be loaded
        :param version: version name, leave blank to load the latest version
        :return: loaded Modelable object
        :rtype: Modelable
        """
        # assert isinstance(model, Model)
        if not version:
            version = self._storage.get_obj(self._get_key(model_class, 'latest'))

        logger.info('Loading model class %s version %s ....' % model_class, version)

        try:
            temp_dir, serdes_dir, tar_file = _make_temp_serdes_dir()

            with open(tar_file, 'wb') as f:
                f.write(self._storage.get_bytes(
                    self._get_key(model_class, version)
                ))

            _tar_extract(tar_file, serdes_dir)
            model_object = self._serdes.deserialize(model_class, serdes_dir)
            model_object.version = version
        finally:
            # We get error from Tensorflow telling that it could not find the folder
            # Unsuccessful TensorSliceReader constructor: Failed to get matching files on
            # /var/folders/wb/40304xlx477cfjzbk386l2gr0000gn/T/tmpwcrvm2e2/model/weights:
            # Not found: /var/folders/wb/40304xlx477cfjzbk386l2gr0000gn/T/tmpwcrvm2e2/model; No such file or directory [Op:RestoreV2]
            #
            # dir_util.remove_tree(temp_dir)

            # instead, register the function to clean it up when the interpreter quits
            import atexit

            def clean_temp_dir(temp_dir):
                # print('Clean up %s'  % temp_dir)
                dir_util.remove_tree(temp_dir)

            atexit.register(clean_temp_dir, temp_dir=temp_dir)
        
        return model_object

    def delete_model(self, model_class, version):
        """
        Delete a model from model repository

        :param model_class:
        :param version: target version
        """
        # assert isinstance(model, Model) or isinstance(model, type)
        assert version != 'latest'  # magic key
        self._storage.delete(self._get_key(model_class, version))

    def download_model(self, model_class, version, target_path):
        """
        Download a model archive (e.g., from S3) to local disk

        :param model_class: 
        :param version: version name
        :param target_path: target folder to extract the model archive
        """
        with tempfile.NamedTemporaryFile(mode="wb") as f:
            f.write(self._storage.get_bytes(
                self._get_key(model_class, version)
            ))
            f.flush()
            f.seek(0)

            _tar_extract(f.name, target_path)

        return target_path

    # TODO: list all versions

    def _get_key(self, model_class, version) -> str:
        """
        Generate a unique key string for the given 'model_class' and 'version'

        :rtype: str
        """
        model_name = model_class.__module__ + '.' + model_class.__name__

        key = f"{model_name}{SEP}{version}"

        if self._NAMESPACE:
            key = f"{self._NAMESPACE}{SEP}{key}"

        return key

    @classmethod
    def get_instance(cls, repository_path=None) -> 'ModelRepository':
        """
        Retrieve the model repository

        :param repository_path: repository path to persist models. Ignored if instance already exists.
        :returns: Model repository singleton instance
        """

        if ModelRepository._singleton:
            return ModelRepository._singleton

        # Check environment variable
        if not repository_path:
            repository_path = os.environ.get('H1ST_MODEL_REPOSITORY_PATH', '')

        # Check config file at root folder
        if not repository_path:
            try:
                import config
                repository_path = config.MODEL_REPOSITORY_PATH
            except ModuleNotFoundError:
                repository_path = None
    
        # Check config file somewhere in module path
        if not repository_path:
            # root module
            root_module_name = ''

            # find the first folder containing config.py to get MODEL_REPO_PATH
            for sub in ModelRepository.__class__.__module__.split('.'):
                root_module_name = sub if not root_module_name else root_module_name + '.' + sub
    
                try:
                    module = importlib.import_module(root_module_name + ".config")
                    repository_path = getattr(module, 'MODEL_REPOSITORY_PATH', None)
                    break
                except ModuleNotFoundError:
                    repository_path = None
    
        if not repository_path:
            raise RuntimeError('Please set H1ST_MODE_REPOSITORY_PATH env variable, or MODEL_REPOSITORY_PATH in config.py')

        ModelRepository._singleton = ModelRepository(repository_path = repository_path)

        return ModelRepository._singleton


def _tar_create(target, source):
    """
    Helper function to create a tar archive
    """
    with tarfile.open(target, "w:gz") as tf:
        tf.add(source, arcname='', recursive=True)

    return target


def _tar_extract(source, target):
    """
    Helper function to extract a tar archive
    """
    with tarfile.open(source) as tf:
        tf.extractall(target)

def _make_temp_serdes_dir():
    temp_dir = tempfile.mkdtemp()
    tar_file = os.path.join(temp_dir, 'model.tar')
    serdes_dir = os.path.join(temp_dir, 'serialized')
    os.makedirs(serdes_dir)
    return temp_dir, serdes_dir, tar_file
