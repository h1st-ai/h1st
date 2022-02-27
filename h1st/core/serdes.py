from abc import ABC
from typing import Dict, Any
import joblib, tempfile


class SerDes(ABC):
    @classmethod
    def do_serialize(cls, obj: Any) -> Any:
        # TODO: implement
        pass

    @classmethod
    def do_deserialize(cls, src: Any) -> Any:
        # TODO: implement
        pass


class JobLibSerDes(SerDes):
    @classmethod
    def do_serialize(cls, obj: Any) -> Any:
        """
        :param obj: object to be serialized (to disk)
        :returns: file object of file containing (compressed) serialized object
        """
        # spool to RAM up to 1MB, for speed
        file_object = tempfile.SpooledTemporaryFile(max_size = 1000000, suffix = ".gz")
        joblib.dump(obj, file_object)
        
        # dump directly to temporary file
        #file_object = tempfile.NamedTemporaryFile(suffix = ".gz", delete = False)
        #import os
        #joblib.dump(obj, os.path.abspath(file_object.name))

        return file_object
    
    @classmethod
    def do_deserialize(cls, src_file_object: str) -> Any:
        """
        :param src_file_object: file object containing compressed, serialized object
        :returns: deserialized object
        """
        # Read from file object, e.g., spooled in RAM
        if hasattr(src_file_object, "name") and not src_file_object.name.endswith(".gz"):
            src_file_object.name += ".gz"

        obj = joblib.load(src_file_object) 

        # Read from temporary file
        #import os
        #fn = os.path.abspath(src_file_object.name)
        #obj = joblib.load(fn)

        return obj