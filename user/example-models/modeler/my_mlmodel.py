from typing import Dict, Any
import __init__
from sklearn.ensemble import RandomForestClassifier
from sklearn import datasets
from h1st.model.ml_model import MLModel

if __name__ == "__main__":
    modeler = MLModel.get_modeler(RandomForestClassifier(n_estimators=10))

    iris = datasets.load_iris()
    model = modeler.train_model({'features': iris.data, 'label': iris.target})
    
    repo_path = "/Users/khoama/Workspace/Aitomatic"
    modeler.persist_model(model, 'my_ml_model_id', repo_path)

    result = model.predict({'features': iris.data})
    print(result)

    model = modeler.load_model('my_ml_model_id', repo_path)
    result = model.predict({'features': iris.data})
    print(result)