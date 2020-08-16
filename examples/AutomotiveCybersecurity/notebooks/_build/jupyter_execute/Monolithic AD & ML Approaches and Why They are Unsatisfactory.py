# 2. Monolithic AD & ML Approaches and Why They are Unsatisfactory

Given the abundance of normal driving data, the problem naturally leads to an anomaly detection (AD) formulation. Let’s try some off-the-shell well-known methods for example Isolation Forest!

In theory, AD approach isn't affected by the Cold Start problem as training data is normal data only, and is hence we only need labels during evaluation of the intrusion detection system.

But will it work accurately enough? Let's try!

### 2a. A naive AD approach using IsolationForest

SENSORS = ["SteeringAngle", "CarSpeed", "YawRate", "Gx", "Gy"]

def compute_timediff_fillna(df):
    df = df.copy()
    for s in SENSORS:
        sensor_not_isna = df[~df[s].isna()]
        df["%s_TimeDiff" % s] = sensor_not_isna.Timestamp - sensor_not_isna.shift(1).Timestamp
    #print(df.head(20))

    for s in SENSORS:
        df[s] = df[s].fillna(method="ffill")
        df["%s_TimeDiff" % s] = df["%s_TimeDiff" % s].fillna(method="ffill")
    df.dropna(inplace=True)
    
    return df

df = pd.read_parquet("%s/train/attacks/20181113_Driver1_Trip1-0.parquet" % DATA_LOCATION)
df = compute_timediff_fillna(df)

Since we know that message timing is important, we should try to use those features in AD training. Can you spot see the difference between normal vs attack messages?

df_normal = df[df.Label == 'Normal']
df_normal.sample(5)

df_attack = df[df.Label == 'Attack']
df_attack.sample(5)

from sklearn.ensemble import IsolationForest
import sklearn.metrics

FEATURES = SENSORS + ["%s_TimeDiff" % s for s in SENSORS]

iforest = IsolationForest(n_estimators=500).fit(df_normal[FEATURES])

df2 = pd.read_parquet("%s/train/attacks/20181203_Driver1_Trip10-20.parquet" % DATA_LOCATION)
df2 = compute_timediff_fillna(df2)

ypred = iforest.predict(df2[FEATURES])
ypred = pd.Series(np.maximum(-ypred, 0))

cf = sklearn.metrics.confusion_matrix(df2.Label == "Attack", ypred)
print(cf) 

print("Accuracy = %s " % sklearn.metrics.accuracy_score(df2.Label =="Attack", ypred))

This is certainly not bad for a start. But the TPR and FPR is no where near what’s needed for deployment!

While there are a lot of exciting approaches for AD and sequential time-series data, including using RNN/LSTM/CNN, autoencoders, self-supervised learning, etc. The fundamental problem with AD is that it is hard to achieve high TPR while simultaneously achieving very low FPR.

Since AD after all, is a harder problem than supervised learning and while they are important parts of the tool box, we still need final human clearance to key system decisions.

### 2b. Machine teaching: leveraging ML to "program" a classifier by specifying human-generated outputs

If we zoom in, it is perhaps easier to see the zig-zag patterns of alternating real vs injected messages. It's clear that perhaps we can leverage a ML to classify these kinds of smooth vs zig-zag patterns.

After all, ML should excel at pattern recognition.

The significance of this approach is that it is much easier for human experts to synthesize the attack data than to write the detection program. And such is the promise of Software 2.0, but will it work?

import matplotlib.pyplot as plt
df[(df.Timestamp >= 200) & (df.Timestamp <= 330)].YawRate.dropna().plot()
plt.title("An period with both normal and attacks of YawRate, can you tell which is which?")
plt.show()

df[(df.Timestamp > 315) & (df.Timestamp < 316)].YawRate.dropna().plot()
plt.title("An attack window on YawRate, zooming in to show zig-zagging between real vs injected values ")
plt.show()

Let’s try a gradient-boosted trees firstly, e.g. sklearn’s HistGradientBoostingClassifier can work well on larger dataset before bringing out bigger guns.

from sklearn.experimental import enable_hist_gradient_boosting
from sklearn.ensemble import HistGradientBoostingClassifier

gbc = HistGradientBoostingClassifier(max_iter=500).fit(df[FEATURES], df.Label == "Attack")

ypred = gbc.predict(df2[FEATURES])

cf = sklearn.metrics.confusion_matrix(df2.Label == "Attack", ypred)
print(sklearn.metrics.accuracy_score(df2.Label == "Attack", ypred))
print(cf)

print("Accuracy = %s " % sklearn.metrics.accuracy_score(df2.Label == "Attack", ypred))

### 2c. Deep Learning and using a H1ST Model API, organizing, importing, saving & loading

We can bring out larger guns like Bidirectional LSTM or CNN or Transformers which can work well on pattern recognition problems on sequential data such as this one. One such model is available in the full tutorial source code package, and it can reach quite impressive accuracy.

Let's see how we could use it!

import h1st as h1
h1.init()

from AutomotiveCybersecurity.models.blstm_injection_msg_classifier import BlstmInjectionMsgClassifier

m = BlstmInjectionMsgClassifier()

A data-science project in H1ST.AI is designed to be a Python-importable package. You can create such a project using the `h1` command-line tool.

Organizing model code this way makes it easy to use as we will see. The Model API provides a unified workflow so that models can be used interactively in notebooks as well as in structured and complex projects as we shall see later.

Here, we call `h1.init()` to make sure we can import the package in our notebooks even when the package is not installed (as long as the notebooks are within the project folder structure).

It is a simple matter to import and train such organized `h1st.Model`, say on a small fraction of the data.

data = m.load_data(num_files=100)

prepared_data = m.prep_data(data)

m.train(prepared_data, epochs=10)

As expected, powerful deep learning models can recognize these attack patterns well. (And we haven’t even trained the model on all the data and until fully converged.)

However, we must reckon that these models, after all, are recognizing attack patterns that humans are generating and injecting artificially. While this is convenient to generate output and train the detector program a la “Software 2.0”, for our situation, because the attacks are purely synthetic, we cannot be too sure that they are learning the right things and work robustly and can be trusted to deploy in the field. It’s best to employ them in the right deployment scope, namely useful pattern recognizers.