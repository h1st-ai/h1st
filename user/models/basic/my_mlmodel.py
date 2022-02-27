import __init__
from sklearn.ensemble import RandomForestClassifier
from sklearn import datasets
from h1st.model.ml_model import MLModel

if __name__ == "__main__":
    modeler = MLModel.get_modeler(RandomForestClassifier(n_estimators=10))

    iris = datasets.load_iris()
    model = modeler.train_model({'features': iris.data, 'label': iris.target})
    
    result = model.predict({'features': iris.data})
    print(result)

    repo_path = "/tmp/my_mlmodel"
    modeler.persist_model(model, 'my_mlmodel_id', repo_path)

    model = modeler.load_model('my_mlmodel_id', repo_path)
    result = model.predict({'features': iris.data})
    print(result)