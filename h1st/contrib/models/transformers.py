"""
Source: https://keras.io/examples/nlp/neural_machine_translation_with_transformer/
"""
import os
from pathlib import Path
import random
import string
import re
import numpy as np
import pickle
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.layers.experimental.preprocessing import TextVectorization

from ...model.ml_model import MLModel

class TransformerEncoder(layers.Layer):
    def __init__(self, embed_dim, dense_dim, num_heads, **kwargs):
        super(TransformerEncoder, self).__init__(**kwargs)
        self.embed_dim = embed_dim
        self.dense_dim = dense_dim
        self.num_heads = num_heads
        self.attention = layers.MultiHeadAttention(
            num_heads=num_heads, key_dim=embed_dim
        )
        self.dense_proj = keras.Sequential(
            [layers.Dense(dense_dim, activation="relu"), layers.Dense(embed_dim),]
        )
        self.layernorm_1 = layers.LayerNormalization()
        self.layernorm_2 = layers.LayerNormalization()
        self.supports_masking = True

    def call(self, inputs, mask=None):
        if mask is not None:
            padding_mask = tf.cast(mask[:, tf.newaxis, tf.newaxis, :], dtype="int32")
        attention_output = self.attention(
            query=inputs, value=inputs, key=inputs, attention_mask=padding_mask
        )
        proj_input = self.layernorm_1(inputs + attention_output)
        proj_output = self.dense_proj(proj_input)
        return self.layernorm_2(proj_input + proj_output)


class PositionalEmbedding(layers.Layer):
    def __init__(self, sequence_length, vocab_size, embed_dim, **kwargs):
        super(PositionalEmbedding, self).__init__(**kwargs)
        self.token_embeddings = layers.Embedding(
            input_dim=vocab_size, output_dim=embed_dim
        )
        self.position_embeddings = layers.Embedding(
            input_dim=sequence_length, output_dim=embed_dim
        )
        self.sequence_length = sequence_length
        self.vocab_size = vocab_size
        self.embed_dim = embed_dim

    def call(self, inputs):
        length = tf.shape(inputs)[-1]
        positions = tf.range(start=0, limit=length, delta=1)
        embedded_tokens = self.token_embeddings(inputs)
        embedded_positions = self.position_embeddings(positions)
        return embedded_tokens + embedded_positions

    def compute_mask(self, inputs, mask=None):
        return tf.math.not_equal(inputs, 0)


class TransformerDecoder(layers.Layer):
    def __init__(self, embed_dim, latent_dim, num_heads, **kwargs):
        super(TransformerDecoder, self).__init__(**kwargs)
        self.embed_dim = embed_dim
        self.latent_dim = latent_dim
        self.num_heads = num_heads
        self.attention_1 = layers.MultiHeadAttention(
            num_heads=num_heads, key_dim=embed_dim
        )
        self.attention_2 = layers.MultiHeadAttention(
            num_heads=num_heads, key_dim=embed_dim
        )
        self.dense_proj = keras.Sequential(
            [layers.Dense(latent_dim, activation="relu"), layers.Dense(embed_dim),]
        )
        self.layernorm_1 = layers.LayerNormalization()
        self.layernorm_2 = layers.LayerNormalization()
        self.layernorm_3 = layers.LayerNormalization()
        self.supports_masking = True

    def call(self, inputs, encoder_outputs, mask=None):
        causal_mask = self.get_causal_attention_mask(inputs)
        if mask is not None:
            padding_mask = tf.cast(mask[:, tf.newaxis, :], dtype="int32")
            padding_mask = tf.minimum(padding_mask, causal_mask)

        attention_output_1 = self.attention_1(
            query=inputs, value=inputs, key=inputs, attention_mask=causal_mask
        )
        out_1 = self.layernorm_1(inputs + attention_output_1)

        attention_output_2 = self.attention_2(
            query=out_1,
            value=encoder_outputs,
            key=encoder_outputs,
            attention_mask=padding_mask,
        )
        out_2 = self.layernorm_2(out_1 + attention_output_2)

        proj_output = self.dense_proj(out_2)
        return self.layernorm_3(out_2 + proj_output)

    def get_causal_attention_mask(self, inputs):
        input_shape = tf.shape(inputs)
        batch_size, sequence_length = input_shape[0], input_shape[1]
        i = tf.range(sequence_length)[:, tf.newaxis]
        j = tf.range(sequence_length)
        mask = tf.cast(i >= j, dtype="int32")
        mask = tf.reshape(mask, (1, input_shape[1], input_shape[1]))
        mult = tf.concat(
            [tf.expand_dims(batch_size, -1), tf.constant([1, 1], dtype=tf.int32)],
            axis=0,
        )
        return tf.tile(mask, mult)

class Seq2SeqTransformer(MLModel):
    def __init__(self, vocab_size = 15000, 
                       sequence_length = 20, 
                       batch_size = 64, 
                       embed_dim=256, 
                       latent_dim=2048, 
                       num_heads = 8,
                       **kwargs
                    ):
        self.sequence_length = sequence_length
        self.vocab_size = vocab_size
        self.batch_size = batch_size
        encoder_inputs = keras.Input(shape=(None,), dtype="int64", name="encoder_inputs")
        x = PositionalEmbedding(sequence_length, vocab_size, embed_dim)(encoder_inputs)
        encoder_outputs = TransformerEncoder(embed_dim, latent_dim, num_heads)(x)
        encoder = keras.Model(encoder_inputs, encoder_outputs)

        decoder_inputs = keras.Input(shape=(None,), dtype="int64", name="decoder_inputs")
        encoded_seq_inputs = keras.Input(shape=(None, embed_dim), name="decoder_state_inputs")
        x = PositionalEmbedding(sequence_length, vocab_size, embed_dim)(decoder_inputs)
        x = TransformerDecoder(embed_dim, latent_dim, num_heads)(x, encoded_seq_inputs)
        x = layers.Dropout(0.5)(x)
        decoder_outputs = layers.Dense(vocab_size, activation="softmax")(x)
        decoder = keras.Model([decoder_inputs, encoded_seq_inputs], decoder_outputs)

        decoder_outputs = decoder([decoder_inputs, encoder_outputs])
        
        self.base_model = keras.Model(
            [encoder_inputs, decoder_inputs], decoder_outputs, name="transformer"
        )

    def load_data(self, text_file, verbose=True):
        
        with open(text_file) as f:
            lines = f.read().split("\n")[:-1]
        text_pairs = []
        for line in lines:
            eng, spa = line.split("\t")
            spa = "[start] " + spa + " [end]"
            text_pairs.append((eng, spa))

        random.shuffle(text_pairs)
        num_val_samples = int(0.15 * len(text_pairs))
        num_train_samples = len(text_pairs) - 2 * num_val_samples
        train_pairs = text_pairs[:num_train_samples]
        val_pairs = text_pairs[num_train_samples : num_train_samples + num_val_samples]
        test_pairs = text_pairs[num_train_samples + num_val_samples :]

        if verbose:
            print(f"{len(text_pairs)} total pairs")
            print(f"{len(train_pairs)} training pairs")
            print(f"{len(val_pairs)} validation pairs")
            print(f"{len(test_pairs)} test pairs")

        return train_pairs, val_pairs, test_pairs

    def prep_data(self, data):
        train_pairs, val_pairs = data
        
        self.strip_chars = self.strip_chars.replace("[", "")
        self.strip_chars = self.strip_chars.replace("]", "")


        def custom_standardization(input_string):
            lowercase = tf.strings.lower(input_string)
            return tf.strings.regex_replace(lowercase, "[%s]" % re.escape(self.strip_chars), "")


        self.eng_vectorization = TextVectorization(
            max_tokens=self.vocab_size, output_mode="int", output_sequence_length=self.sequence_length,
        )

        self.spa_vectorization = TextVectorization(
            max_tokens=self.vocab_size,
            output_mode="int",
            output_sequence_length=self.sequence_length + 1,
            standardize=custom_standardization,
        )
        train_eng_texts = [pair[0] for pair in train_pairs]
        train_spa_texts = [pair[1] for pair in train_pairs]


        self.eng_vectorization.adapt(train_eng_texts)
        self.spa_vectorization.adapt(train_spa_texts)
        def format_dataset(eng, spa):
            eng = self.eng_vectorization(eng)
            spa = self.spa_vectorization(spa)
            return ({"encoder_inputs": eng, "decoder_inputs": spa[:, :-1],}, spa[:, 1:])


        def make_dataset(pairs):
            eng_texts, spa_texts = zip(*pairs)
            eng_texts = list(eng_texts)
            spa_texts = list(spa_texts)
            dataset = tf.data.Dataset.from_tensor_slices((eng_texts, spa_texts))
            dataset = dataset.batch(self.batch_size)
            dataset = dataset.map(format_dataset)
            return dataset.shuffle(2048).prefetch(16).cache()


        train_ds = make_dataset(train_pairs)
        val_ds = make_dataset(val_pairs)

        return train_ds, val_ds
    
    def train(self, data, epochs=30):
        train_ds, val_ds = data

        self.base_model.summary()
        self.base_model.compile(
            "rmsprop", loss="sparse_categorical_crossentropy", metrics=["accuracy"]
        )

        self.base_model.fit(train_ds, epochs=epochs, validation_data=train_ds)

    def persist(self, version):
        home = str(Path.home())
        model_path = f"{home}/.models/{version}/model"
        os.makedirs(model_path, exist_ok=True)

        # # Pickle the English Vectorization's config and weights
        # config, weights = self.eng_vectorization.get_config(), self.eng_vectorization.get_weights()
        # pickle.dump({'config': config,
        #             'weights': weights}
        #             , open(f"{version}/ev_layer.pkl", "wb"))

        # # Pickle the Spanish Vectorization's config and weights
        # config, weights = self.spa_vectorization.get_config(), self.spa_vectorization.get_weights()
        # pickle.dump({'config': config,
        #             'weights': weights}
        #             , open(f"{version}/sv_layer.pkl", "wb"))

        
        self.base_model.save(model_path)

    def load(self, version):

        # ev_layer = pickle.load(open(f"{version}/ev_layer.pkl", "rb"))
        # self.eng_vectorization = TextVectorization.from_config(ev_layer['config'])
        # # You have to call `adapt` with some dummy data (BUG in Keras)
        # new_v.adapt(tf.data.Dataset.from_tensor_slices(["xyz"]))
        # self.eng_vectorization.set_weights(ev_layer['weights'])

        # spa_layer = pickle.load(open(f"{version}/sv_layer.pkl", "rb"))
        # self.spa_vectorization = TextVectorization.from_config(spa_layer['config'])
        # # You have to call `adapt` with some dummy data (BUG in Keras)
        # new_v.adapt(tf.data.Dataset.from_tensor_slices(["xyz"]))
        # self.spa_vectorization.set_weights(spa_layer['weights'])

        train_pairs, val_pairs, _ = self.load_data(verbose=False)
        train_ds, val_ds = self.prep_data(data=(train_pairs, val_pairs))

        home = str(Path.home())
        model_path = f"{home}/.models/{version}/model"
        self.base_model = tf.saved_model.load(model_path)

    def predict(self, data):
        from google.cloud import translate_v2 as translate
        translate_client = translate.Client()
        result = translate_client.translate(data,
                                            source_language='en',
                                            target_language='es')
        return result['translatedText']

    def predict2(self, text):
        spa_vocab = self.spa_vectorization.get_vocabulary()
        spa_index_lookup = dict(zip(range(len(spa_vocab)), spa_vocab))
        max_decoded_sentence_length = 20


        def decode_sequence(input_sentence):
            tokenized_input_sentence = self.eng_vectorization([input_sentence])
            decoded_sentence = "[start]"
            result = []
            for i in range(max_decoded_sentence_length):
                tokenized_target_sentence = self.spa_vectorization([decoded_sentence])[:, :-1]
                predictions = self.base_model([tokenized_input_sentence, tokenized_target_sentence])

                sampled_token_index = np.argmax(predictions[0, i, :])
                sampled_token = spa_index_lookup[sampled_token_index]
                decoded_sentence += " " + sampled_token
                result.append(sampled_token)

                if sampled_token == "[end]":
                    break
            return ' '.join(result[:-1])

        # return decode_sequence(text)

        import six
        if isinstance(text, six.binary_type):
            text = text.decode("utf-8")
        
        from google.cloud import translate_v2 as translate
        result = translate.Client().translate(text, target_language='spa')
        return result['translatedText']