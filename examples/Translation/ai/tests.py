from mock_framework import GoogleLanguageTranslationModel, HuggingFaceLanguageTranslationModel

def test_google_translation():
    model = GoogleLanguageTranslationModel()
    assert model.predict(text='Hello', target='de') == 'Hallo'

def test_hugging_face_translation():
    model = HuggingFaceLanguageTranslationModel('en', 'de')
    assert model.predict('Hello') == 'Hallo'