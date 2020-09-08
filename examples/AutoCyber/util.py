import random
import s3fs
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
    fs = s3fs.S3FileSystem(anon=False)
    train_normal_files = ['s3://' + f for f in fs.glob(config.AUTOCYBER_DATA_PATH + "/train/Normal/*.csv", recursive=True)]
    train_attack_files = ['s3://' + x for x in fs.glob(config.AUTOCYBER_DATA_PATH + "/train/Attack/*/*.csv", recursive=True)]
    test_normal_files = ['s3://' + x for x in fs.glob(config.AUTOCYBER_DATA_PATH + "/test/public/Normal/*.csv", recursive=True)]
    test_attack_files = ['s3://' + x for x in fs.glob(config.AUTOCYBER_DATA_PATH + "/test/public/Attack/*/*.csv", recursive=True)]
    if shuffle:
        random.shuffle(train_normal_files)
        random.shuffle(train_attack_files)
        random.shuffle(test_normal_files)
        random.shuffle(test_attack_files)
    if num_files:
        return {
            'train_normal_files': train_normal_files[:num_files], 
            'train_attack_files': train_attack_files[:num_files],
            'test_normal_files': test_normal_files[:num_files],
            'test_attack_files': test_attack_files[:num_files]
        }
    return {
        'train_normal_files': train_normal_files, 
        'train_attack_files': train_attack_files,
        'test_normal_files': test_normal_files,
        'test_attack_files': test_attack_files
    }

def compute_timediff_fillna(df):
    df = df.copy()
    for s in config.SENSORS:
        sensor_not_isna = df[~df[s].isna()]
        df["%s_TimeDiff" % s] = sensor_not_isna.Timestamp - sensor_not_isna.shift(1).Timestamp
    #print(df.head(20))

    for s in config.SENSORS:
        df[s] = df[s].fillna(method="ffill")
        df["%s_TimeDiff" % s] = df["%s_TimeDiff" % s].fillna(0.)
    df.dropna(inplace=True)
    
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
        df = pd.read_csv(f)
        df.columns = ['Timestamp', 'Label', 'CarSpeed', 'SteeringAngle', 'YawRate', 'Gx', 'Gy']
        result = graph.predict({"df": df})
            
        event_preds = []
        event_labels = []
        for event_result in result["event_detection_results"]:
            pred = event_result['WindowInAttack']
            event_preds.append(pred)

            in_window = (df.Timestamp >= event_result['window_start']) & (df.Timestamp < event_result['window_start'] + config.WINDOW_SIZE)
            w_df = df[in_window]
            label = np.any(w_df.Label == "Tx")
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
