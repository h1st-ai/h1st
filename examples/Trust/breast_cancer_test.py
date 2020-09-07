from breast_cancer import BreastCancer

model = BreastCancer()
data = model.load_data()
prepared_data = model.prep_data(data)
model.train(prepared_data)
evaluation = model.evaluate(prepared_data)
# print(evaluation)

describer = model.describe()

# print(describer.shap_describer.shap_values)
idx = 4
decision_input = model.prepared_data["train_df"].iloc[idx]

explainer = model.explain(decision_input=decision_input, constituent=10, aspect=10)
print(explainer.decision_describer)
