import __init__
from h1st.model.boolean_model import BooleanModel

class UserBooleanModel(BooleanModel):
    def process(self, input_data: dict):
        x = input_data["x"]
        if x > 0.5:
            return True
        else:
            return False


def run_user_boolean_model():
    """
    Specifies the API requirements for h1st.model.BooleanModel
    """
    m = UserBooleanModel()
    print(m.__class__.__name__ + ".process() returned", m.process({"x": 1}))
    print(m.__class__.__name__ + ".process() returned", m.process({"x": 0}))
    print(m.__class__.__name__ + ".predict() returned", m.predict({"x": 1}))
    print(m.__class__.__name__ + ".predict() returned", m.predict({"x": 0}))

run_user_boolean_model()
