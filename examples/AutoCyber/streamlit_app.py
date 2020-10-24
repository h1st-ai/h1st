import streamlit as st
import time
import numpy as np
import pandas as pd

@st.cache
def get_data():
    AWS_BUCKET_URL = "s3://h1st-tutorial-autocyber/attack-samples"
    df = pd.read_parquet(AWS_BUCKET_URL + "/20181114_Driver2_Trip1-0.parquet")
    return df

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
print(attk_events)

import random
eid = random.choice(attk_events)
print(eid)
df = df[df.AttackEventIndex == eid]

SENSORS = ["SteeringAngle", "CarSpeed", "YawRate", "Gx", "Gy"]
attack_sensor = st.selectbox("Select a sensor to attack", SENSORS)

import matplotlib.pyplot as plt
z = df.dropna(subset=[attack_sensor])
normal = z[z["Label"] == "Normal"]
fig = plt.figure()
plt.plot(normal.Timestamp, normal[attack_sensor], label="normal %s" % attack_sensor)
plt.legend()
st.write(fig)

# Streamlit widgets automatically run the script from top to bottom. Since
# this button is not connected to any other logic, it just causes a plain
# rerun.
st.button("Re-run")