from h1st.model.oracle.oracle import Oracle
from h1st.model.oracle.teacher import Teacher

class MyOracle(Oracle):
    class MyTeacher(Teacher):
        def predict(self, input_data: dict) -> dict:
            x = input_data["x"]
            prediction = (x > 0.5)
            return {"prediction": prediction}

    def __init__(self):
        super().__init__(Teacher())
