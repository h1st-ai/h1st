import sys
import h1st.core.utils as utils


class Serializable:
    """
    Support for self-serdes by classes such as Model, so that they can be safely
    transported across the wire for, e.g., distributed/remoting deployments.
    """

    @property
    def serialized_data(self):
        if getattr(self, "__serialized_data", None) is None:
            self.serialized_data = {}
        return getattr(self, "__serialized_data")

    @serialized_data.setter
    def serialized_data(self, value):
        setattr(self, "__serialized_data", value)


    def add_serialized_data(self, property_name, value=None):
        if value is None:
            self.add_serialized_data(property_name, getattr(self, property_name, utils.class_name(None)))
        else:
            self.serialized_data[property_name] = value
    
    def pre_serialize(self):
        """
        Override to do housekeeping work just before Serialize()
        """


    def __do_serialize(self, obj):
        result = obj.serialize() if isinstance(obj, Serializable) else None
        return result


    def serialize(self):
        """
        Optional override to serialize known `Serializable` members in your class.
        """
        if getattr(self, "__is_being_serialized", None):
            return None
        setattr(self, "__is_being_serialized", True)

        self.pre_serialize()

        self.add_serialized_data("class_name", utils.class_name(self))

        # Take care of all properies that are Serializable or list of Serializables
        for attr in dir(self):
            if hasattr(self, attr):
                obj = getattr(self, attr)
                obj = obj if isinstance(obj, list) else [obj]
                for item in obj:
                    self.__do_serialize(item)

        self.post_serialize()

        delattr(self, "__is_being_serialized")

        return self.serialized_data


    def post_serialize(self):
        """
        Override to do housekeeping work just after Serialize()
        """


    @classmethod
    def pre_deserialize(cls, serialized_data):
        """
        Override to do housekeeping work just before Deserialize()
        Note that this is a class method, since we do not yet have a (deserialized) instance.
        """


    @classmethod
    def deserialize(cls, serialized_data):
        """
        Takes a dictionary `serialized_data` and deserializes all the values into their named properties.
        Note that this is a class method, since we do not yet have a (deserialized) instance.
        """
        instance = None
        full_class_name = serialized_data["class_name"]
        if full_class_name is not None:
            words = full_class_name.split(".")
            module_name = ".".join(words[:-1])
            class_name = words[-1:][0]
            the_class = getattr(sys.modules[module_name], class_name)
            instance = the_class()

        return instance


    def post_deserialize(self):
        """
        Override to do housekeeping work just after Deserialize()
        """
