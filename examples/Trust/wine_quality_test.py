from wine_quality import WineQuality

model = WineQuality()
data = model.load_data()
prepared_data = model.prep_data(data)
model.train(prepared_data)
evaluation = model.evaluate(prepared_data)
model.model.__getattribute__()
# print(evaluation)

# describer = model.describe()
# print(describer)
# idx = 4
# sample_input = model.prepared_data["train_df"].iloc[idx]
# # print(sample_input)
# explainer = model.explain(decision=sample_input)
# print(explainer)
