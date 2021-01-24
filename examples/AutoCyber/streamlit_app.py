import streamlit as st
import time
import numpy as np
import pandas as pd

from aegis_datagen import build_constant_val_msg_stream

@st.cache
def get_data():
    AWS_BUCKET_URL = "s3://h1st-tutorial-autocyber/attack-samples"
    df = pd.read_parquet(AWS_BUCKET_URL + "/20181114_Driver2_Trip1-0.parquet")
    return df

def do_injection(df, sensor_name, values, period):
    df = df.copy()
    
    dt = df["Timestamp"].max() - df["Timestamp"].min()

    start = df["Timestamp"].min()
    end = df["Timestamp"].max()
    
    value_start = df[df["Timestamp"] < start][sensor_name].fillna(method="ffill").fillna(method="bfill").values
    value_start = value_start[-1]
    
    value = 0.0
    rows = build_constant_val_msg_stream(value, start, end, period=period, value_jitter=0./20.)
    dfinj = pd.DataFrame.from_records(rows, columns =['Timestamp', sensor_name])

    dfinj["Label"] = "Attack"
    dfinj["AttackSensor"] = sensor_name
    dfinj["AttackMethod"] = method
    dfinj["AttackParams"] = scale

    # # # double check time diff / msg freq of injected values
    # actual_period = (dfinj["Timestamp"] - dfinj["Timestamp"].shift(1)).mean() * 1000
    # assert np.abs(period - actual_period) / period < 0.05, "unexpected injection msg freq, actual_period = %s" % actual_period
        
    df2 = pd.concat([df, dfinj]).sort_values("Timestamp")

    # these values always go together   
    if sensor_name in ("YawRate", "Gx", "Gy"):
        df2_filled = df2.fillna(method="ffill")
        df2.loc[df2.Label == "Attack", ["YawRate", "Gx", "Gy"]] = df2_filled.loc[df2_filled.Label == "Attack", ["YawRate", "Gx", "Gy"]]

    if DEBUG: print("injected %s rows, before = %s, after = %s" % (len(dfinj), len(df), len(df2)))
    # print(df2)
    return df2, start, end

try:
    df = get_data()
    print(df.head())
except Exception as e:
    st.error(
        """
        **This demo requires internet access.**

        Connection error: %s
    """
        % e
    )

attk_events = df.AttackEventIndex.dropna().unique()
print("unique attk_events = %s" % attk_events)

import random
eid = st.selectbox("Select an sample index", attk_events)
df = df[df.AttackEventIndex == eid]

SENSORS = ["SteeringAngle", "CarSpeed", "YawRate", "Gx", "Gy"]
attack_sensor = st.selectbox("Select a sensor to attack", SENSORS)

import matplotlib.pyplot as plt
z = df.dropna(subset=[attack_sensor])
normal = z[z["Label"] == "Normal"]
fig = plt.figure(figsize=(9, 3))
plt.plot(normal.Timestamp, normal[attack_sensor], label="normal %s" % attack_sensor)
plt.legend()
# plt.savefig("out.png")

st.write(fig)


import streamlit as st
from PIL import Image
from streamlit_drawable_canvas import st_canvas

attack_msg_freq = st.sidebar.slider("Attack msg period (ms)", 12, 96, 24, step=12)
attack_msg_timing = st.sidebar.slider("Attack msg time jitter (ns)", 500, 5000, 1000, step=500)

drawing_mode = st.sidebar.selectbox(
    "Drawing tool:", ("freedraw", "line")
)

canvas_result = st_canvas(
    # fill_color="rgba(255, 165, 0, 0.3)",  # Fixed fill color with some opacity
    stroke_width=2,
    #stroke_color=stroke_color,
    background_color="transparent",
    #background_image=Image.open("out.png"),
    update_streamlit=True,
    height=240,
    width=600,
    drawing_mode=drawing_mode,
    key="canvas",
)

if canvas_result.image_data is not None:
    print("canvas_result.image_data")
    print(type(canvas_result.image_data))
    print(canvas_result.image_data.shape) # shape (240, 600, 4)
    x = canvas_result.image_data[:,:,3]
    print(x.shape)
    print(x)
    values = np.argmax(x, axis=0)
    print("Raw values")
    print(values)
    values = (255 - values)/255.0
    values = pd.Series(values)
    values = values.replace(1.0, float("NaN"))
    print("pd.Series values")
    print(values)
    zmax, zmin = z[attack_sensor].max(), z[attack_sensor].min()
    print((zmax, zmin))
    values = values * (zmax - zmin) + zmin
    st.write("Scaled values")
    st.write(values)


import matplotlib.pyplot as plt
z = df.dropna(subset=[attack_sensor])
normal = z[z["Label"] == "Normal"]
fig = plt.figure(figsize=(9, 3))
plt.plot(normal.Timestamp, normal[attack_sensor], label="normal %s" % attack_sensor)
plt.legend()
# plt.savefig("out.png")

st.write(fig)


# Streamlit widgets automatically run the script from top to bottom. Since
# this button is not connected to any other logic, it just causes a plain
# rerun.
st.button("Re-run")