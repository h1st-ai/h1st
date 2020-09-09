from wine_quality import WineQuality

model = WineQuality()
data = model.load_data()
prepared_data = model.prep_data(data)
model.train(prepared_data)
# evaluation = model.evaluate(prepared_data)

# # print(evaluation)

# describer = model.describe()
# print(describer.shap_describer.shap_values.shape)
# idx = 4
# decision = model.prepared_data["train_df"].iloc[idx], model.prepared_data["train_labels"].iloc
# # print(sample_input)
# explainer = model.explain(decision=decision)
# print(explainer.decision_describer)
