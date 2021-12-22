from h1st.model.model import Model

class RuleBasedModel(Model):
    def predict(self, input_data: dict) -> dict:
        return self.proccess(input_data=input_data)

