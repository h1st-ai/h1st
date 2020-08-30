from unittest import TestCase
import h1st as h1
import h1st.core.utils as utils

class AModel(h1.Model):
    property_a = "property_a"
    property_b = "property_b"

    def serialize(self):
        self.add_serialized_data("property_a")
        self.parameters = {"test_name" : "test_value"}
        result = super().serialize()

        return result


class SerializeableModelTestCase(TestCase, h1.Model):

    the_thing = AModel()

    def setUp(self):
        self._sub_models = [AModel(), AModel()]

    def test_serialize(self):
        result = self.serialize()

        self.assertIsInstance(self.the_thing.serialized_data, dict)
        self.assertEqual(self.the_thing.serialized_data["class_name"], utils.class_name(self.the_thing))
        for model in self._sub_models:
            self.assertIsInstance(model.serialized_data, dict)
            self.assertEqual(model.serialized_data["class_name"], utils.class_name(model))
        self.assertIsInstance(self.serialized_data, dict)
        self.assertEqual(self.serialized_data["class_name"], utils.class_name(self))

    def test_deserialize(self):
        instance = h1.Model.deserialize({"class_name": utils.class_name(self)})
        self.assertIsInstance(instance, SerializeableModelTestCase)