import datetime
import random
import pandas as pd
import numpy as np

# +
DEBUG = False

def add_timestamp_noise(CarSpeed, noise_scale):
    # convert back to int
    CarSpeed["Timestamp"] = (CarSpeed["Timestamp"] - t0).dt.total_seconds()

    # add noise
    CarSpeed["Timestamp_w_noise"] = CarSpeed["Timestamp"] + np.random.normal(loc=0.0, scale=noise_scale, size=len(CarSpeed["Timestamp"]))

    # compute time diff stats
    if DEBUG: print((CarSpeed.Timestamp_w_noise - CarSpeed.Timestamp_w_noise.shift(1)).describe())

    # convert to timestamp for joining
    CarSpeed['Timestamp'] = pd.to_datetime(CarSpeed['Timestamp_w_noise'], unit="s")
    del CarSpeed['Timestamp_w_noise']
    
    return CarSpeed


# -

def verify_msg_freq(ts_speed):
    ts_speed = result[~result["CarSpeed"].isna()]["Timestamp"]
    if not (ts_speed - ts_speed.shift(1)).mean() - 0.024 < 0.0001:
        print("WARNING: unexpected CarSpeed msg freq")
        
    ts_steering = result[~result["SteeringAngle"].isna()]["Timestamp"]
    if not (ts_steering - ts_steering.shift(1)).mean() - 0.012 < 0.0001:
        print("WARNING: unexpected CarSpeed msg freq")
    
    ts_YR = result[~result["YawRate"].isna()]["Timestamp"]
    if not (ts_YR - ts_YR.shift(1)).mean() - 0.012 < 0.0001:
        print("WARNING: unexpected YawRate msg freq")


def build_constant_val_msg_stream(value, start, end, period, time_jitter=500, value_jitter=0.1):
  rows = []
  t = start
  assert time_jitter<period*1000
  while t < end:
    t += period/1000 + int(random.uniform(-time_jitter, time_jitter))/1e6
    if t < end:
        if value_jitter:
            rows.append((t, value + random.random()*value_jitter))
        else:
            rows.append((t, value))
  return rows


def build_increasing_val_msg_stream(value, start, end, period, time_jitter=500, method="tanh", scale=1.0):
  rows = []
  t = start
  assert time_jitter<period*1000
  while t < end:
    t += period/1000 + int(random.uniform(-time_jitter, time_jitter))/1e6
    value_jitter = random.uniform(-1., 1.) * 0.01
    if t < end:
        if method == "tanh":
            if value < 1e-3:
                value = 1
            rows.append((t, value*(1+np.tanh((t-start)*3 + value_jitter)*scale)))
        elif method == "linear":
            rows.append((t, value + (t-start)*scale + value_jitter))
        elif method == "quadratic":
            if value < 1e-3:
                value = 1
            rows.append((t, value*(1+np.square((t-start)/3 + value_jitter)*scale)))
  return rows


def do_injection(df, sensor_name, scale, period, max_attack_dt=20., method="const", limit=None):
    df = df.copy()
    
    dt = df["Timestamp"].max() - df["Timestamp"].min()
    attack_pct = random.uniform(0.25, 0.65)
    attack_dt = dt * attack_pct
    attack_dt = min(attack_dt, max_attack_dt)
    if DEBUG: print("attack_pct = %.2f, attack_dt = %.2f second" % (attack_pct, attack_dt))
    start = random.uniform(df["Timestamp"].min() + 3., df["Timestamp"].min() + attack_dt)
    end = start + attack_dt
    if DEBUG: print("injection start, end = %.3f, %3.f" % (start, end))
    
    value_start = df[df["Timestamp"] < start][sensor_name].fillna(method="ffill").fillna(method="bfill").values
    value_start = value_start[-1]
    
    if method == "const":
        value = scale
        rows = build_constant_val_msg_stream(value, start, end, period=period, value_jitter=scale/20.)
        dfinj = pd.DataFrame.from_records(rows, columns =['Timestamp', sensor_name])         
    elif method == "noise":
        dfinj = df[(df["Timestamp"] <= end) & (df["Timestamp"] >= start)]
        dfinj = dfinj[~dfinj[sensor_name].isna()].copy()
        # print(dfinj)
        dfinj[sensor_name] += np.random.normal(scale=scale*dfinj[sensor_name].max(), size=len(dfinj))
        dfinj["Timestamp"] += random.uniform(0, 12)/1e6 # time shift
        dfinj["Timestamp"] += np.random.uniform(0, 4, size=len(dfinj))/1e6 # jitter
        # print(dfinj)
    elif method == "duplicate":
        # simply a timing shift, msg-value are copied from last known
        dfinj = df[(df["Timestamp"] <= end) & (df["Timestamp"] >= start)]
        dfinj = dfinj[~dfinj[sensor_name].isna()].copy()
        # print(dfinj)
        dfinj["Timestamp"] += random.uniform(0, 12)/1e6 # time shift
        dfinj["Timestamp"] += np.random.uniform(0, 4, size=len(dfinj))/1e6 # jitter
    elif method == "linear":
        rows = build_increasing_val_msg_stream(value_start, start, end, period=period, method="linear", scale=scale)
        dfinj = pd.DataFrame.from_records(rows, columns =['Timestamp', sensor_name])         
    elif method == "tanh":
        rows = build_increasing_val_msg_stream(value_start, start, end, period=period, method="tanh", scale=scale)
        dfinj = pd.DataFrame.from_records(rows, columns =['Timestamp', sensor_name])         
    elif method == "quadratic":
        rows = build_increasing_val_msg_stream(value_start, start, end, period=period, method="quadratic", scale=scale)
        dfinj = pd.DataFrame.from_records(rows, columns =['Timestamp', sensor_name])         

    dfinj["Label"] = "Attack"
    dfinj["AttackSensor"] = sensor_name
    dfinj["AttackMethod"] = method
    dfinj["AttackParams"] = scale

    # # double check time diff / msg freq of injected values
    actual_period = (dfinj["Timestamp"] - dfinj["Timestamp"].shift(1)).mean() * 1000
    assert np.abs(period - actual_period) / period < 0.05, "unexpected injection msg freq, actual_period = %s" % actual_period
    
    # truncate to abs limit
    if limit:
        dfinj[sensor_name] = np.maximum(dfinj[sensor_name], np.ones_like(dfinj[sensor_name]) * limit["low"])
        dfinj[sensor_name] = np.minimum(dfinj[sensor_name], np.ones_like(dfinj[sensor_name]) * limit["high"])
    
    df2 = pd.concat([df, dfinj]).sort_values("Timestamp")

    if DEBUG: print("injected %s rows, before = %s, after = %s" % (len(dfinj), len(df), len(df2)))
    # print(df2)
    return df2, start, end


def do_sensor_injection(df, sensor, plot=True, saveplot_filename=None):
    meth = random.choice(list(PARAMS[sensor]["method"]))
    x0, x1 = PARAMS[sensor]["method"][meth]
    limit = PARAMS[sensor]["limit"]
    period = PARAMS[sensor]["period"]
    scale = random.uniform(x0, x1)
    if DEBUG: print("meth, scale = %s, %.2f" % (meth, scale))
    
    dfi, start, end = do_injection(df, sensor, period=period, scale=scale, method=meth, limit=limit)
    
    if plot or saveplot_filename:
        att = dfi[dfi["Label"]=="Attack"][sensor]    
        t_att = dfi[dfi["Label"]=="Attack"]["Timestamp"]
        nor = dfi[dfi["Label"]=="Normal"][sensor].fillna(method="ffill")
        t_nor = dfi[dfi["Label"]=="Normal"]["Timestamp"]
        plt.figure()
        plt.plot(t_nor, nor, '-', label="normal")
        plt.plot(t_att, att, '+', label="attack", alpha=0.1)
        plt.ylim(limit['low'], dfi[sensor].max()*1.25)
        plt.legend()
        if saveplot_filename:
            plt.savefig(saveplot_filename)
        if plot:
            plt.show()
    return dfi, start, end


PARAMS = {'CarSpeed': {'limit': {'high': 200.0, 'low': 0},
  'period': 24,
  'method': {'const': [30, 100],
   'noise': [0.025, 0.1],
   'linear': [0.2, 1.5],
   'quadratic': [0.1, 0.5],
   'tanh': [0.5, 1.5],
   'duplicate': [0.0, 0.0]}},
 'SteeringAngle': {'limit': {'high': 720.0, 'low': 0},
  'period': 12,
  'method': {'const': [30, 100],
   'noise': [0.025, 0.1],
   'linear': [0.2, 1.5],
   'quadratic': [0.1, 0.5],
   'tanh': [0.5, 1.5],
   'duplicate': [0.0, 0.0]}},
 'YawRate': {'limit': {'high': 40.0, 'low': 0},
  'period': 12,
  'method': {'const': [30, 100],
   'noise': [0.025, 0.1],
   'linear': [0.2, 1.5],
   'quadratic': [0.1, 0.5],
   'tanh': [0.5, 1.5],
   'duplicate': [0.0, 0.0]}},
 'Gx': {'limit': {'high': 4.0, 'low': -4.0},
  'period': 12,
  'method': {'const': [30, 100],
   'noise': [0.025, 0.1],
   'linear': [0.2, 1.5],
   'quadratic': [0.1, 0.5],
   'tanh': [0.5, 1.5],
   'duplicate': [0.0, 0.0]}},
 'Gy': {'limit': {'high': 4.0, 'low': -4.0},
  'period': 12,
  'method': {'const': [30, 100],
   'noise': [0.025, 0.1],
   'linear': [0.2, 1.5],
   'quadratic': [0.1, 0.5],
   'tanh': [0.5, 1.5],
   'duplicate': [0.0, 0.0]}}}

# +
import os
import matplotlib.pyplot as plt

def synthesize_attacks(df, num_passes, sensor=None, chunk_dt=30., chunk_attk_proba=0.25, plot=False):
    results = []
    df["Label"] = "Normal"
    dt = df["Timestamp"].max() - df["Timestamp"].min()
    print("n = %s, dt = %s" % (len(df), dt))
    j = 0
    for n_pass in range(num_passes):
        if dt > chunk_dt:
            chunks = []
            for i in range(int(dt//chunk_dt)):
                # chunk attack proba is 0.25
                dfsub = df[(df["Timestamp"] > df["Timestamp"].min() + i*chunk_dt) &
                           (df["Timestamp"] < df["Timestamp"].min() + (i+1)*chunk_dt)].copy()
                dfsub["AttackSensor"] = "NA"
                dfsub["AttackMethod"] = "NA"
                dfsub["AttackParams"] = 0.0
                dfsub["AttackEventIndex"] = "NA"
                if random.random() < chunk_attk_proba:
                    j += 1
                    chunk_name = "%.2f..%.2f" % ( dfsub["Timestamp"].min(), dfsub["Timestamp"].max() )
                    if sensor is None:
                        attk_sensor = random.choice(list(PARAMS.keys()))
                    else:
                        attk_sensor = sensor
                    # fname = "%s-%s-%s-%s" % (os.path.basename(f).replace(".parquet", ""), n_pass, chunk_name, sensor)
                    # saveplot_filename = "%s/plots/%s.png" % (output_dir, fname)
                    # print("saving chunk plot to %s" % saveplot_filename)
                    try:
                        dfi, start, end = do_sensor_injection(dfsub, attk_sensor, plot=plot)
                    except IndexError:
                        continue    
                    # Event-level label
                    dfi.loc[(dfi.Timestamp >= start) & (dfi.Timestamp <= end), "AttackEventIndex"] = j
                    chunks.append(dfi)
                else:
                    chunks.append(dfsub)
            dfi = pd.concat(chunks, axis=0).reset_index()
            del dfi['index']
            # fname = "%s/%s-%s.parquet" % (output_dir, os.path.basename(f).replace(".parquet", ""), n_pass)
            # print("saving %s" % fname)
            # dfi.to_parquet("%s" % fname, index=False)
            results.append(dfi)
    return results

