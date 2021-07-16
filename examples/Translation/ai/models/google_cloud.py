class Model():
    def predict(self, *args, **kwargs):
        pass

class MLModel(Model):
    def predict(self, *args, **kwargs):
        pass

class LanguageTranslationModel(MLModel):
    def predict(self, *args, **kwargs):
        pass

class GoogleLanguageTranslationModel(LanguageTranslationModel):
    def predict(self, text, target, *args, **kwargs):
        import six
        from google.cloud import translate_v2 as translate

        # The key should be specified in the environment, for example
        # export GOOGLE_APPLICATION_CREDENTIALS=airy-timing-314804-1fa11fcc2bd3.json
        translate_client = translate.Client()
    
        if isinstance(text, six.binary_type):
            text = text.decode("utf-8")
    
        # Text can also be a sequence of strings, in which case this method
        # will return a sequence of results for each text.
        result = translate_client.translate(text, target_language=target)
    
        # print(u"Text: {}".format(result["input"]))
        # print(u"Translation: {}".format(result["translatedText"]))
        # print(u"Detected source language: {}".format(result["detectedSourceLanguage"]))
        return result['translatedText']

class HuggingFaceLanguageTranslationModel(LanguageTranslationModel):
    def __init__(self, source, target):
        # Init the model
        self.model = None
        from transformers import pipeline
        if source == 'en' and target == 'de':
            self.model = pipeline("translation_en_to_de")
    def predict(self, text, max_length=40, *args, **kwargs):
        return self.model(text, max_length=max_length)[0]['translation_text']
