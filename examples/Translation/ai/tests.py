from models.google_cloud import GoogleLanguageTranslationModel, HuggingFaceLanguageTranslationModel
from models.en2spa_transformer import En2SpaSeq2SeqTransformer

from h1st.contrib.quality.neuron_coverage import TFNeuronCoverage1, TFNeuronCoverage2

def test_google_translation():
    model = GoogleLanguageTranslationModel()
    assert model.predict(text='Hello', target='de') == 'Hallo'

def test_hugging_face_translation():
    model = HuggingFaceLanguageTranslationModel('en', 'de')
    assert model.predict('Hello') == 'Hallo'

def test_En2Spa_transformer_translation():

    model = En2SpaSeq2SeqTransformer()
    model_version = 'v2'
    train_pairs, val_pairs, _ = model.load_data()
    train_ds, val_ds = model.prep_data(data=(train_pairs, val_pairs))

    # This will take ~ 20 minute per epoch on CPU
    model.train(data=(train_ds, val_ds), epochs=10)
    model.persist(model_version)

def test_En2Spa_transformer_translation_prediction():

    model = En2SpaSeq2SeqTransformer()
    model_version = 'v2'
    model.load(model_version)

    print(model.predict('Hello'))

def test_neuron_coverage():
    model = En2SpaSeq2SeqTransformer()
    train_pairs, val_pairs, test_pairs = model.load_data()
    nc1 = TFNeuronCoverage1()
    nc1.gen_diff(seeds=test_pairs, model=model)
