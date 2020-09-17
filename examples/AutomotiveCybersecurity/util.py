import glob
import os
import pathlib
import random
import urllib.request
import zipfile

import pandas as pd
import numpy as np
import sklearn.metrics

import AutomotiveCybersecurity.config as config


def gen_windows(df, window_size, step_size):
    window_start = df['Timestamp'].min()
    max_timestamp = df['Timestamp'].max()
    # df_len = (max_timestamp - window_start)
    # print('Data length: %.4f seconds' % df_len)
    while window_start + window_size <= max_timestamp:
        yield window_start
        window_start += step_size


def load_data(num_files=None, shuffle=False):
    pathlib.Path("data").mkdir(parents=True, exist_ok=True)

    # check 2 files, check files count later
    if not os.path.isfile('data/driving-trips/20181113_Driver1_Trip1.parquet') or not os.path.isfile('data/attack-samples/20181203_Driver1_Trip10-0.parquet'):
        print('Fetching https://h1st-tutorial-autocyber.s3.amazonaws.com/h1st_autocyber_tutorial_data.zip ...')
        with urllib.request.urlopen('https://h1st-tutorial-autocyber.s3.amazonaws.com/h1st_autocyber_tutorial_data.zip') as f:
            content = f.read()
        with open('data/h1st_autocyber_tutorial_data.zip', 'wb') as f:
            f.write(content)
        with zipfile.ZipFile('data/h1st_autocyber_tutorial_data.zip', 'r') as zip_ref:
            zip_ref.extractall("data")

    normal_files = glob.glob('data/driving-trips/*.parquet', recursive=True)
    attack_files = glob.glob('data/attack-samples/*.parquet', recursive=True)

    if num_files is None and ((len(normal_files) != 21) or (len(attack_files) != 9)):
        raise RuntimeError("unexpected number of files found, please clear the 'data' folder and rerun load_data()")

    if shuffle:
        random.shuffle(normal_files)
        random.shuffle(attack_files)
    if num_files:
        return {
            'normal_files': normal_files[:num_files], 
            'attack_files': attack_files[:num_files],
        }
    return {
        'normal_files': normal_files, 
        'attack_files': attack_files,
    }

def compute_timediff_fillna(df, dropna_subset=None):
    df = df.copy()
    for s in config.SENSORS:
        sensor_not_isna = df[~df[s].isna()]
        df["%s_TimeDiff" % s] = sensor_not_isna.Timestamp - sensor_not_isna.shift(1).Timestamp
    #print(df.head(20))

    for s in config.SENSORS:
        df[s] = df[s].fillna(method="ffill")
        df["%s_TimeDiff" % s] = df["%s_TimeDiff" % s].fillna(-1) # method="ffill")
    if dropna_subset:
        df.dropna(subset=dropna_subset, inplace=True)
    
    return df


def compute_tpr_fpr(tn, fp, fn, tp):
    if (tp + fn) > 0:
        tpr = tp / (tp + fn)
    else:
        tpr = float('nan')
    if (fp + tn) > 0:
        fpr = fp / (fp + tn)
    else:
        fpr = float('nan')
    return tpr, fpr


def evaluate_event_graph(graph, files):
    TN, FP, FN, TP = 0, 0, 0, 0 # event level
    
    for f in files:
        # print(f)
        df = pd.read_parquet(f)
        result = graph.predict({"df": df})
            
        event_preds = []
        event_labels = []
        for event_result in result["event_detection_results"]:
            pred = event_result['WindowInAttack']
            event_preds.append(pred)

            in_window = (df.Timestamp >= event_result['window_start']) & (df.Timestamp < event_result['window_start'] + config.WINDOW_SIZE)
            w_df = df[in_window]
            label = np.any(w_df.Label == config.ATTACK_LABEL)
            event_labels.append(label)
        dfw = pd.DataFrame({"WindowLabel": event_labels, "WindowInAttack": event_preds})

        cf  = sklearn.metrics.confusion_matrix(dfw["WindowLabel"], 
                                               dfw["WindowInAttack"])
        # print("Event cf")
        # print(cf)
        if len(cf) > 1:
            a, b, c, d = cf.ravel()
            TN += a; FP += b; FN += c; TP += d
        else:
            TP += cf.ravel()[0]
        # print("Event TPR = %.4f, FPR = %.4f" % compute_tpr_fpr(a, b, c, d))
    
    print("============")
    print("Event-level confusion matrix")
    print(np.array([[TN, FP], [FN, TP]]))
    print("Event TPR = %.4f, FPR = %.4f" % compute_tpr_fpr(TN, FP, FN, TP))

    return (TN, FP, FN, TP)
