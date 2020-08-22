import h1st as h1


class AbcModel(h1.Model):
    def get_data(self):
        # Implement code to retrieve your data here
        return dict()

    def prep_data(self, data):
        # Implement code to prepare your data here
        return data

    def train(self, prepared_data):
        # Implement your train method
        raise NotImplementedError()

    def evaluate(self, data):
        raise NotImplementedError()

    def predict(self, data):
        # Implement your predict function
        raise NotImplementedError()
