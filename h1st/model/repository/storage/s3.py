from typing import Any, NoReturn
import cloudpickle
import s3fs
from h1st.model.repository.storage.base import Storage


class S3Storage(Storage):
    """
    Provide data storage on top of AWS S3
    """

    def __init__(self, bucket_name: str = "", prefix: str = ""):
        """
        :param bucket_name: s3 bucket name to store data into
        :param prefix: s3 object prefix, leave blank to store at bucket root
        """
        self.bucket_name = bucket_name
        self.prefix = prefix
        self.fs = s3fs.S3FileSystem()

    def get_obj(self, name: str) -> Any:
        """
        Retrieve object value

        :param name: object name
        """
        key = self._to_key(name)
        try:
            with self.fs.open(key, 'rb') as f:
                return cloudpickle.load(f)
        except FileNotFoundError as ex:
            raise KeyError(name) from ex

    def get_bytes(self, name) -> bytes:
        """
        Retrieve object value in bytes

        :param name: object name
        """
        key = self._to_key(name)
        try:
            with self.fs.open(key, 'rb') as f:
                return f.read()
        except FileNotFoundError as ex:
            raise KeyError(name) from ex

    def set_obj(self, name: str, value: Any) -> NoReturn:
        """
        Set key value to a python object

        :param name: object name
        :param value: value in python object
        """
        key = self._to_key(name)

        with self.fs.open(key, 'wb') as f:
            return cloudpickle.dump(value, f)

    def set_bytes(self, name: str, value: bytes) -> NoReturn:
        """
        Set a key value to a list of bytes

        :param name: object name
        :param value: value in bytes
        """
        key = self._to_key(name)

        with self.fs.open(key, 'wb') as f:
            f.write(value)

    def exists(self, name: str) -> bool:
        """
        Return true if object exists in the storage
        """
        key = self._to_key(name)
        return self.fs.exists(key)

    def delete(self, name: str) -> NoReturn:
        """
        Delete an object in storage
        """
        try:
            key = self._to_key(name)
            self.fs.rm(key)
        except FileNotFoundError:
            pass

    def _to_key(self, key):
        """
        Convert a key to s3 object key with bucket and prefix
        """
        key = key.replace("/", "_").replace("::", "/")

        if self.prefix:
            key = f"{self.prefix}/{key}"

        return f"{self.bucket_name}/{key}"
