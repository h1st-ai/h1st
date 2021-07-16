from ..model import Model as H1stModel


class GoogleCloudTranslateModel(H1stModel):
    def predict(self, text, src_lang='en', target_lang='es'):
        from google.cloud import translate_v2 as translate

        translate_client = translate.Client()

        result = translate_client.translate(text,
                                            source_language=src_lang,
                                            target_language=target_lang)

        return result['translatedText']
