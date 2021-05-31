from ai.models.google_cloud import GoogleLanguageTranslationModel, HuggingFaceLanguageTranslationModel
from ai.models.en2spa_transformer import En2SpaSeq2SeqTransformer

def test_google_translation():
    model = GoogleLanguageTranslationModel()
    assert model.predict(text='Hello', target='de') == 'Hallo'

def test_hugging_face_translation():
    model = HuggingFaceLanguageTranslationModel('en', 'de')
    assert model.predict('Hello') == 'Hallo'

def test_En2Spa_transformer_translation():

    model = En2SpaSeq2SeqTransformer()
    # model_folder = 'En2SpaSeq2SeqTransformer'
    train_pairs, val_pairs, _ = model.load_data()
    train_ds, val_ds = model.prep_data(data=(train_pairs, val_pairs))

    # This will take ~ 20 minute per epoch
    model.train(data=(train_ds, val_ds))
    # model persistence does not work for now
    # model.persist(model_folder)

    model.predict('She handed him the money')
