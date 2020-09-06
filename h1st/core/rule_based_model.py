import h1st as h1

class RuleBasedModel(h1.Model):

    def predict(self, input_data: dict) -> dict:
        raise NotImplementedError(input_data)
