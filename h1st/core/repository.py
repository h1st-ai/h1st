#from msilib.schema import File
import os
import tarfile
import tempfile
import logging
import importlib
from distutils import dir_util

import ulid

from .serializable import Serializable

from .storage.s3 import S3Storage
from .storage.local import LocalStorage

SEP = "::"
logger = logging.getLogger(__name__)


class Repository:
    """
    Repository allows user to persist and load objects to different storage systems.

    Given a Serializable object to persist, we first use SerDes to serialize it to local disk,
    then copy it to the destination storage system.

    Loading performs the reverse.
    """

    _DEFAULT_REPOSITORY_PATH = "/tmp/h1st/repository"
    _NAMESPACE = "_objects"
    _singleton = None


    @classmethod
    def get_instance(cls, repository_path = None) -> 'Repository':
        return Repository._singleton or Repository(repository_path)


    def __init__(self, repository_path = None):
        if not repository_path:
            repository_path = self._get_default_repository_path()

        #self._NAMESPACE = ""
        if  "s3://" in repository_path:
            repository_path = repository_path.replace("s3://", "").strip("/") + "/"
            bucket, prefix = repository_path.split("/", 1)
            self._storage = S3Storage(bucket, prefix.strip("/"))
        else:
            self._storage = LocalStorage(repository_path)


    def persist_object(self, obj: Serializable, version=None) -> str:
        """
        Save an oject the repository

        :param object:
        :param version: version name, leave blank for autogeneration
        :return: version name
        :rypte: str
        """
        # TODO: use version format: v_20200714-1203
        if not obj:
            return None

        obj_class = obj.__class__
        version = version or str(ulid.new())

        try:
            # serialize the to a temporary place
            file = obj.to_file()

            # copy serialized bytes from temp to permanent storage
            key = self._get_key(obj_class, version)
            file.seek(0)
            self._storage.set_bytes(key, file.read())
            self._storage.set_obj(key, version)

            #self._storage.set_obj(
            #    self._get_key(obj_class, 'latest'),
            #    version,
            #)

        finally:
            obj.version = version
            # clean up temp
            file.close()
            #dir_util.remove_tree(file)

        return obj.version


    def load_object(self, obj_class, version=None) -> Serializable:
        """
        Restore the model from the model repository

        :param model_class: class of model to be loaded
        :param version: version name, leave blank to load the latest version
        :return: loaded Modelable object
        :rtype: Modelable
        """
        assert issubclass(obj_class, Serializable)

        if not version:
            version = self._storage.get_obj(self._get_key(obj_class, 'latest'))

        logger.info("Loading object class {} version {} ....".format(obj_class.__name__, version))

        try:
            file = tempfile.NamedTemporaryFile()
            key = self._get_key(obj_class, version)

            file.write(self._storage.get_bytes(key))
            file.seek(0)

            loaded_obj = obj_class.from_file(file)
            #setattr(loaded_obj, "version", version)

        finally:
            # We get error from Tensorflow telling that it could not find the folder
            # Unsuccessful TensorSliceReader constructor: Failed to get matching files on
            # /var/folders/wb/40304xlx477cfjzbk386l2gr0000gn/T/tmpwcrvm2e2/model/weights:
            # Not found: /var/folders/wb/40304xlx477cfjzbk386l2gr0000gn/T/tmpwcrvm2e2/model; No such file or directory [Op:RestoreV2]
            #
            # dir_util.remove_tree(temp_dir)

            # instead, register the function to clean it up when the interpreter quits
            #import atexit

            #def clean_temp_dir(temp_dir):
                # print('Clean up %s'  % temp_dir)
            #    dir_util.remove_tree(temp_dir)

            #atexit.register(clean_temp_dir, temp_dir=temp_dir)
            pass
        
        return loaded_obj

    def delete_model(self, model_class, version):
        """
        TODO: update/fix

        Delete a model from model repository

        :param model_class:
        :param version: target version
        """
        # assert isinstance(model, Model) or isinstance(model, type)
        assert version != 'latest'  # magic key
        self._storage.delete(self._get_key(model_class, version))

    def download_model(self, model_class, version, target_path):
        """
        TODO: update/fix

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

    def _get_key(self, obj_class, version) -> str:
        """
        Generate a unique key string for the given 'model_class' and 'version'

        :rtype: str
        """
        model_name = obj_class.__module__ + '.' + obj_class.__name__

        key = f"{model_name}{SEP}{version}"

        if self._NAMESPACE:
            key = f"{self._NAMESPACE}{SEP}{key}"

        return key


    def _get_default_repository_path(self) -> str:
        """
        Look at various places for the H1ST_REPOSITORY_PATH config setting
        """
        # Check environment variable
        repository_path = os.environ.get('H1ST_REPOSITORY_PATH')

        # Check config file at root folder
        if not repository_path:
            try:
                import config
                if hasattr(config, "H1ST_REPOSITORY_PATH"):
                    repository_path = config.H1ST_REPOSITORY_PATH
            except ModuleNotFoundError:
                repository_path = None
    
        # Check config file somewhere in module path
        if not repository_path:
            # root module
            root_module_name = ''

            # find the first folder containing config.py
            for sub in Repository.__class__.__module__.split('.'):
                root_module_name = sub if not root_module_name else root_module_name + '.' + sub
    
                try:
                    module = importlib.import_module(root_module_name + ".config")
                    repository_path = getattr(module, 'H1ST_REPOSITORY_PATH', None)
                    break
                except ModuleNotFoundError:
                    repository_path = None
    
        if not repository_path:
            repository_path = Repository._DEFAULT_REPOSITORY_PATH

        #if not repository_path:
        #    raise RuntimeError('Please set H1ST_REPOSITORY_PATH env variable, or in config.py')

        return repository_path