# USER: Other framework (K1st) and service layer

# WHAT:
# Simple, understandable in less than 5 seconds for the term
# Stressing on Knowledge

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__),'../../'))

from h1st.model import model

class MySimpleModel(model.Model):
    def predict(self, input_data):
        return input_data

if __name__ == "__main__":
    m = MySimpleModel()
    print(m.predict({"x": 1}))
    print(m.predict({"x": 0}))