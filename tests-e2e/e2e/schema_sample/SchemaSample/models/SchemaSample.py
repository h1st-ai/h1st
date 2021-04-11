import h1st.core as h1

class SchemaSampleModel(h1.Model):
    def get_data(self):
        # Implement code to retrieve your data here
        return dict()

    def prep(self, data):
        # Implement code to prepapre your data here
        return data

    def train(self, prep):
        # Implement your train method
        raise NotImplementedError()

    def evaluate(self, data):
        raise NotImplementedError()

    def predict(self, data):
        # Implement your predict function
        return {
            'results': sum(data['inputs'])
        }
