import os
import re
from typing import Any, NoReturn
import cloudpickle
from azure.storage import blob
from azure.storage.blob import BlobServiceClient
from h1st.model.repository.storage.base import Storage
from h1st.exceptions.exception import UnconfiguredEnvironmentException


class AzureBlobStorage(Storage):
    """
    Provide data storage on top of Azure Blob storage
    """
    URI_PATTERN = (r"https://(?P<account>[^\.]+)\.blob\.core\.windows\.net/"
                   r"(?P<bucket>[^/]+)/(?P<prefix>[^?]+)"
                   r"(?:[?{1}](?P<token>\S+))?")

    def __init__(self, bucket_name: str = "", prefix: str = ""):
        """
        :param bucket_name: s3 bucket name to store data into
        :param prefix: s3 object prefix, leave blank to store at bucket root
        """
        connection_string = os.getenv('AZURE_CONNECTION_STRING')
        if connection_string is None:
            raise UnconfiguredEnvironmentException(
                'Must set the evironment variable AZURE_CONNECTION_STRING in '
                'order to user Azure blob as the model repository.'
            )

        self.bucket_name = bucket_name
        self.prefix = prefix
        self.connection_string = connection_string

        self.service_client = BlobServiceClient.from_connection_string(
                self.connection_string
        )
        self.client = self.service_client.get_container_client(bucket_name)

    @classmethod
    def from_url(cls, url: str) -> AzureBlobStorage:
        """
        parse azure blob url to return storage object

        :param url: azure uri to model repository in the form
        https://<account_name>.blob.code.windows.net/<container>/<prefix>
        """
        try:
            tokens = re.match(cls.URI_PATTERN, url).groupdict()
            bucket_name = tokens['bucket']
            prefix = tokens['prefix']
        except AttributeError as ex:
            correct = ('https://<account_name>.blob.code.windows.net'
                       '/<container>/<prefix>')
            raise ValueError(f'Invalid azure URL format.\n{url}\ndoes not '
                             f'match\n{correct}')
        except KeyError as ex:
            correct = ('https://<account_name>.blob.code.windows.net'
                       '/<container>/<prefix>')
            raise ValueError(f'Invalid azure URL format.\n{url}\ndoes not '
                             f'match\n{correct}') from ex

        return cls(bucket_name, prefix)

    def get_obj(self, name: str) -> Any:
        """
        Retrieve object value

        :param name: object name
        """
        return cloudpickle.loads(self.get_bytes(name))

    def get_bytes(self, name) -> bytes:
        """
        Retrieve object value in bytes

        :param name: object name
        """
        key = self._to_key(name)
        try:
            blob = self.client.get_blob_client(blob=key)
            downloader =  blob.download_blob()
            return downloader.readall()
        except FileNotFoundError as ex:
            raise KeyError(name) from ex

    def set_obj(self, name: str, value: Any) -> NoReturn:
        """
        Set key value to a python object

        :param name: object name
        :param value: value in python object
        """
        return self.set_bytes(name, cloudpickle.dumps(value))

    def set_bytes(self, name: str, value: bytes) -> NoReturn:
        """
        Set a key value to a list of bytes

        :param name: object name
        :param value: value in bytes
        """
        key = self._to_key(name)
        blob = self.client.get_blob_client(blob=key)
        return blob.upload_blob(values)

    def exists(self, name: str) -> bool:
        """
        Return true if object exists in the storage
        """
        key = self._to_key(name)
        blob = self.client.get_blob_client(blob=key)
        return blob.exists()

    def delete(self, name: str) -> NoReturn:
        """
        Delete an object in storage
        """
        try:
            key = self._to_key(name)
            blob = self.client.get_blob_client(blob=key)
            blob.delete_blob()
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
