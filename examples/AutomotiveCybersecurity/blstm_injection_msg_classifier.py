import glob
import random

import s3fs
import tensorflow as tf 
import pandas as pd
import numpy as np
import h1st as h1

import config
import util


def create_model(rnn_size=128, lr=1e-3, clip_norm=10., n_sensors=5, classif=True, multilabel=False, compile=True):
    if classif and not multilabel:
        n_outputs = 1
    else:
        n_outputs = n_sensors
    model = tf.keras.Sequential([
              tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(rnn_size, recurrent_dropout=0.0,
                                           dtype=tf.float32,
                                           return_sequences=True)),
              tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(rnn_size//2, recurrent_dropout=0.0,
                                           dtype=tf.float32,
                                           return_sequences=True)),
              tf.keras.layers.Dense(rnn_size,
                                    activation="relu",
                                    dtype=tf.float32),
              tf.keras.layers.Dense(n_outputs,
                                    activation="sigmoid" if classif else "linear",
                                    dtype=tf.float32),
            ])

    lr_schedule = tf.keras.optimizers.schedules.ExponentialDecay(
        lr,
        decay_steps=20000,
        decay_rate=0.95)

    if compile:
        if classif:
            model.compile(optimizer=tf.optimizers.Adam(learning_rate=lr_schedule, clipnorm=1.),
                        loss=tf.keras.losses.BinaryCrossentropy(),
                        metrics=["accuracy",])
        else:
            model.compile(optimizer=tf.optimizers.Adam(learning_rate=lr_schedule, clipnorm=1.),
                        loss=tf.keras.losses.MSE)
    
    return model


NORMALIZATION = {'CarSpeed': {'center': 0.0, 'scale': 68.25},
    'SteeringAngle': {'center': 0.0, 'scale': 493.5},
    'YawRate': {'center': 0.0, 'scale': 18.54400000000001},
    'Gx': {'center': 0.0, 'scale': 1.0408100000000005},
    'Gy': {'center': 0.0, 'scale': 10.58755},
}

def normalize(df):
    df = df.copy()
    for f, norm in NORMALIZATION.items():
        z = (df[f] - norm['center']) / norm['scale']
        # print("transforming %s" % f)
        # print(z)
        df.loc[:, f] = z
    return df


def fillna0_ffill_target(df, filename, SENSORS):
    training = df.copy()
    training = training.sort_values("Timestamp")
    training = training.dropna(how='all', subset=SENSORS)
    # training['TimeDiff'] = (training['Timestamp']-training['Timestamp'].shift()) * 1000
    for c in SENSORS:
        training["%s_is_na"%c] = training[c].isna()

    training["Label"] = (training.Label == config.ATTACK_LABEL)        
    training = training.fillna(0)

    return training


def create_datasets(SENSORS, train_files, val_files, batch_size=32, num_steps=128, classif=True, multilabel=True):
    features = SENSORS + ["%s_is_na"%s for s in SENSORS]
    print("FEATURES = %s" % features)

    fname = random.choice(train_files)
    print("Sample raw data from file %s" % fname)
    df = pd.read_csv(fname)
    df.columns = ['Timestamp', 'Label', 'CarSpeed', 'SteeringAngle', 'YawRate', 'Gx', 'Gy',]

    if np.any(df.Label == config.ATTACK_LABEL):
        df = df[df[df.Label == config.ATTACK_LABEL].index[0]:] # starting from first attack
    print(df.head(20))
    print("Sample transformed features")
    df = fillna0_ffill_target(df, fname, SENSORS)
    print(normalize(df)[features].head(20))
    
    def parse_windows(f):
        f = f.decode("utf-8") # f is bytes, orig from a tf.string tensor
        # if random.random() < 0.25:
        #     raise ValueError("testing error handling branch, should not cause tf.data pipeline to crash")

        # print("reading %s" % f)
        1
        df = pd.read_csv(f)
        df.columns = ['Timestamp', 'Label', 'CarSpeed', 'SteeringAngle', 'YawRate', 'Gx', 'Gy',]

        df = fillna0_ffill_target(df, f, SENSORS)
        # if DEBUG: print(df.head(5))
        # print(df.head(5))
        past_dt = 200.0/1000 # ms
        cur_dt = 100.0/1000
        future_dt = 100.0/1000
        total_dt = past_dt + cur_dt + future_dt
        t = df["Timestamp"].min()            

        pad_to_len = num_steps
        target_col = "Label"

        Xs, ys = [], []
        
        while t <= df["Timestamp"].max():
            z = df[(df["Timestamp"] >= t) & (df["Timestamp"] < t + total_dt)].copy()
            if len(z) < pad_to_len:
                # print("pad extra hist now, len(z) = %s" % len(z))
                z = df[(df["Timestamp"] < t + total_dt)][-pad_to_len:].copy()
                if len(z) < pad_to_len:
                    # # drop this seq for now
                    t += cur_dt
                    continue
                    # print("pad_zeroes now, len(z) = %s" % len(z))
                    # z = pad_zeroes(z, sensors=SENSORS, to_len=pad_to_len)
            # print(z)

            X = normalize(z[features]).values.astype(np.float32)
            y = z["Label"].astype(np.float32)
            Xs.append(X)
            ys.append(y)

            # not cur_dt, for training we ignore overlapping
            t += total_dt
        
        # print([x.shape for x in Xs])
        X = np.stack(Xs)
        y = np.stack(ys)
        # print("X.shape = %s" % X.shape)
        return X, y

    def parse_windows_tf(f):
        X, y = tf.numpy_function(parse_windows, [f], Tout=(tf.float32, tf.float32))
        X.set_shape((None, num_steps, len(features)))
        y.set_shape((None, num_steps))
        ds = tf.data.Dataset.from_tensor_slices((X, y))
        print("ds ret = %s" % ds)
        return ds

    options = tf.data.Options()
    options.experimental_deterministic = False # faster maybe
    
    train_ds = tf.data.Dataset.from_tensor_slices(train_files)\
        .interleave(parse_windows_tf, num_parallel_calls=tf.data.experimental.AUTOTUNE)\
        # .apply(tf.data.experimental.ignore_errors())\
        # .with_options(options)
    val_ds = tf.data.Dataset.from_tensor_slices(val_files)\
        .interleave(parse_windows_tf, num_parallel_calls=tf.data.experimental.AUTOTUNE)\
        # .apply(tf.data.experimental.ignore_errors())\
        # .with_options(options)

    train_ds = train_ds.batch(batch_size).cache().prefetch(tf.data.experimental.AUTOTUNE)
    val_ds = val_ds.batch(batch_size).cache().prefetch(tf.data.experimental.AUTOTUNE)
    
    return train_ds, val_ds


class BlstmInjectionMsgClassifier(h1.Model):
    def __init__(self):
        self.sensors = ['CarSpeed', 'SteeringAngle','YawRate','Gx','Gy']
        self.model = create_model(rnn_size=128, lr=1e-3, clip_norm=10., n_sensors=len(self.sensors), compile=False)
        self.model.build(input_shape=[None, None, len(self.sensors)*2+1])

    def load_data(self, num_files=None, shuffle=True):
        return util.load_data(num_files=num_files, shuffle=shuffle)

    def prep_data(self, data):
        # Implement code to prepapre your data here
        attack_files = data["train_attack_files"]
        random.shuffle(attack_files)
        num_att_train = int(len(attack_files) * 0.95)
        # num_norm_train = int(len(normal_files) * 0.95)
        train_files = attack_files[:num_att_train]
        val_files = attack_files[num_att_train:]
        random.shuffle(train_files)
        print("train_files[:10] = %s" % train_files[:10])
        print("len(train_files) = %s" % len(train_files))
        random.shuffle(val_files)
        print("val_files[:10] = %s" % val_files[:10])
        print("len(val_files) = %s" % len(val_files))
        train_ds, val_ds = create_datasets(SENSORS=self.sensors, train_files=train_files, val_files=val_files, batch_size=64, num_steps=128)
        return train_ds, val_ds

    def train(self, prepared_data, **extra_kwargs):
        # Implement your train method
        train_ds, val_ds = prepared_data
        self.model = create_model(rnn_size=128, lr=1e-3, clip_norm=10., n_sensors=len(self.sensors), compile=True)
        callbacks = [
            # tf.keras.callbacks.CSVLogger('blstm_classif_log.csv', append=True, separator=';'),            
            tf.keras.callbacks.EarlyStopping(monitor='val_loss', min_delta=1e-5, patience=10, verbose=1),
            tf.keras.callbacks.ModelCheckpoint(filepath='checkpoints/blstm_classif{epoch}.h5', 
                                              save_best_only=True, 
                                              monitor='val_loss', 
                                              verbose=1),
            # tf.keras.callbacks.TensorBoard(log_dir='logs/blstm_classif', update_freq=100),
        ]

        try:
            os.system("mkdir %s" % car_model)
            os.system("mkdir %s/checkpoints" % car_model)
        except:
            pass
        kwargs = {"epochs": 100}
        kwargs.update(extra_kwargs)
        history = self.model.fit(train_ds, validation_data=val_ds,  callbacks=callbacks, verbose=1, **kwargs)
        self.history = history
        return self

    def evaluate(self, data):
        raise NotImplementedError()

    def predict(self, data):
        # Implement your predict function
        raise NotImplementedError()
