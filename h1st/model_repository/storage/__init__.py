"""
Storage module

Provide a generic API to interact with different storage system. The storage can
read and write raw bytes or python objects It currently supports local disk and S3.::

   from h1st.model_repository.storage import LocalStorage

   storage = LocalStorage(local_path)
   # save and retrive a dataframe to disk
   storage.set_obj("my_df", pd.DataFrame(...))
   df = storage.get_obj("my_df")


"""

from .local import LocalStorage
from .s3 import S3Storage
