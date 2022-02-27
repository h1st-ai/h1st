import __init__
from typing import Dict
from h1st.model.model import Model

class MyModel(Model):
    def process(self, data: Dict = None) -> Dict:
        return {"key": "value"}

if __name__ == "__main__":
    print("Starting...")

    modeler = MyModel.get_modeler()
    print("Modeler instantiated...", modeler)

    model = modeler.build_model()
    print("Model built...", model)

    result = model.process()
    print("Model process() result", result)

    modeler.persist_model(model, 'my_model_id', "/tmp/my_repository")
    print("Model persisted to /tmp/my_repository", "version: my_model_id")

    loaded_model = modeler.load_model('my_model_id')
    print("Model loaded from /tmp/my_repository", "version: my_model_id")

    result = loaded_model.process()
    print("Model process() result", result)
