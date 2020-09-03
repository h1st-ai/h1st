from h1st.core.trust.explainable import Explainable
def get_model_name(model):
    return str(type(model).__name__)

def get_cosntituent_number(name):
    return Explainable.Constituency[name].value
def get_top_n_features_to_explain_constituent(argument):
    switcher = {
        10: 5,
        20: 3,
        30: 3,
        40: 3,
        50: 3,
        60: 3,
        70: 3,
        99: 5,
        100:5     
    }
    return switcher.get(argument, "Invalid Constituent")