import __init__
from h1st.model.model import Model

class MyModel(Model):
   def process(self):
       return {"key": "value"}


if __name__ == "__main__":
    m = MyModel.get_modeler().build_model()
    result = m.process()
    print(result)