import __init__
from typing import Dict
from h1st.model.model import Model

class MyModel(Model):
    def process(self, data: Dict = None) -> Dict:
        return {"key": "value"}

if __name__ == "__main__":
    modeler = MyModel.get_modeler()

    model = modeler.build_model()

    result = model.process()
    print(result)

    modeler.persist_model(model, 'my_model_id', "/tmp/my_model")

    loaded_model = modeler.load_model('my_model_id')

    result = loaded_model.process()
    print(result)
