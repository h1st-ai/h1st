from wine_quality import WineQuality

model = WineQuality()
data = model.load_data()
prepared_data = model.prep_data(data)
model.train(prepared_data)
evaluation = model.evaluate(prepared_data)

# print(evaluation)

describer = model.describe()
print(describer.shap_describer.shap_values.shape)
idx = 4
decision_input = model.prepared_data["train_df"].iloc[idx]
# print(sample_input)
explainer = model.explain(decision_input=decision_input)
print(explainer.decision_describer)
