"""
Storage module

Provide a generic API to interact with different storage system. The storage can
read and write raw bytes or python objects It currently supports local disk and S3.::

   from h1st.model.repository.storage import LocalStorage

   storage = LocalStorage(local_path)
   # save and retrive a dataframe to disk
   storage.set_obj("my_df", pd.DataFrame(...))
   df = storage.get_obj("my_df")


"""

from h1st.model.repository.storage.local import LocalStorage
from h1st.model.repository.storage.s3 import S3Storage


def create_storage(storage):
    if isinstance(storage, str) and "s3://" in storage:
        storage = storage.replace("s3://", "").strip("/") + "/"
        bucket, prefix = storage.split("/", 1)
        storage = S3Storage(bucket, prefix.strip("/"))
    elif isinstance(storage, str):  # local folder
        storage = LocalStorage(storage)

    return storage
