# 3. Using H1st.AI: Encoding Human Insights as a Model and Harmonizing Human + ML in a H1st.Graph

The H1ST.AI approach to this problem begins by thinking about the end-users of the decision system, and their uses cases.

What are the use cases for such Automotive Cybersecurity system? We can envision two distinctive use cases:
  1. The onboard intrusion detection system can detect an attack event in realtime and set the car into a safe mode so that drivers can safely get to a safe location and not be stuck in the highway with malfunctioning cars.
  2. An security expert could review the attack in post-mortem mode, in which the IDS provides message-by-message attack vs normal classification.

For use case #1 "safe mode triggering by attack event detection", the ML requirement is that it has near-zero FPR. 

To give an example, each second might contain 100 of CAN messages per car. If we have a fleet with just 1000 cars, each driven 1h per day, then a FPR of 0.00001 at message-level still means that each day we have 0.00001 x 100msg x 3600s x 1000cars = 3600 false positive events per day!

Additionally, for deployment & anticipated regulatory purpose, the system should behave robustly and explainably. While explainability is a complex subject, we meant that one could anticipate the system’s behavior reasonably well, as well as for legal/regulation purposes. As we saw with iForest or GBM ML models, they don’t quite meet this requirement, as it is hard to explain precisely how these models classify attacks, even if they can achieve good accuracy.

For use case #2 "post-morterm analysis", it turns out that the requirement is very different. Some FPR could be traded off for higher TPR for post-mortem. And the system might not need to highly explainable as it is after all the jobs of the security experts to analyze the attacks in depth and make the final decisions.

### 3b. Problem (re)formulation into H1st.AI Graph

We reformulate the problem into the form of a decision graph, where the outermost flow detects attack events and corresponding yes branches handles message classification. For this tutorial we focus on injection attacks which are most common in the wild (we will revisit this later).

The graph looks like this.

<img src="http://docs.arimo.com/H1ST_AI_Tutorial/img/graph2.png" alt="automotive cybersecurity solution graph"/>

### 3c. Encoding human insights for event detection as a H1st.Model

Remember when we start analyzing the CAN dataset, we have remarked that the normal data is highly regular, especially in terms of the message frequency for each CAN ID.

It turns out that using message frequency statistics for injection event detection is highly accurate for safe-mode use cases (high TPR, low FNR). This surprising fact was first pointed out by the original CAN bus hackers Chris Valasek and Charlie Miller in the seminal white paper [Adventures in Automotive Networks and Control Units](https://ioactive.com/pdfs/IOActive_Adventures_in_Automotive_Networks_and_Control_Units.pdf).

> It is pretty straightforward to detect the attacks discussed in this paper.  They always involve either sending new, unusual CAN packets or flooding the CAN bus with common packets... Additionally, the frequency of normal CAN packets is very predictable... Therefore we propose that a system can detect CAN anomalies based on the known frequency of certain traffic and can alert a system or user if frequency levels vary drastically from what is well known. 

Using H1ST, we can encode insights of such “human” models and use them just like ML models. An h1.Model is essentially anything that can predict. H1ST provides tools to help automate their saving and loading, too, easing the way for using them in an integrated decision system.

In a H1ST project structure, we typically organize this under `models` directory, e.g. the content of `models/msg_freq_event_detector.py` looks like this.

SENSORS = ["SteeringAngle", "CarSpeed", "YawRate", "Gx", "Gy"]

class MsgFreqEventDetectorModel(h1.Model):
    def load_data():
        pass
    
    def train(data):
        pass
    
    def predict(self, data):
        present_size=0.1
        df = data['df']
        window_starts = data["window_starts"]
        window_results = []
        for window_start in window_starts:
            w_df = df[(df.Timestamp >= window_start) & (df.Timestamp < window_start + WINDOW_SIZE)]
            results = {}
            for _, sensor in enumerate(SENSORS):
                w_df_sensor = w_df.dropna(subset=[sensor])
                max_normal_message_freq = self.stats.at['max', sensor]
                msg_freq = len(w_df_sensor)
                if msg_freq > (max_normal_message_freq+1): #or min_timediff < min_normal_timediff:
                    results[sensor] = 1
                else:
                    results[sensor] = 0
                
                # print((window_start, sensor, msg_freq, max_normal_message_freq, results[sensor]))
                
                results["WindowInAttack"] = any(results.values())
            results["window_start"] = window_start # information for down-stream
            window_results.append(results)
        return {"event_detection_results": window_results}

Now let's import and train this `MsgFreqEventDetectorModel`.

from AutomotiveCybersecurity.models.msg_freq_event_detector import MsgFreqEventDetectorModel

m = MsgFreqEventDetectorModel()

You can look inside the model file `models/msg_freq_event_detector.py` to see the details of training. It’s quite simple, looping through a number of files to compute window statistics such as how many msg per CAN ID are found & what’s the min & max and percentile values.


data = m.load_data(num_samples=20)
m.train(data)

m.stats

The nice things about h1st.Model that we can easily save/load them. By default, the "model", "stats" and "metrics" properties are persisted and they support a variety of flavors & data structure.

m.persist()

### 3d. Working with H1st Graph

Let's now make some event-level predictions.

Note that since the model was persisted using H1st model repo, this means that we can easily come back to a notebooks and/or scripts and load the trained model or computed statistics.

Importantly, H1st allows much speedier integration into a Graph (and later deployment, too).

from AutomotiveCybersecurity.graph import WindowGenerator
from AutomotiveCybersecurity.models.msg_freq_event_detector import MsgFreqEventDetectorModel

graph = h1.Graph()
graph.start()\
     .add(WindowGenerator())\
     .add(MsgFreqEventDetectorModel().load())
graph.end()

import glob
fs = glob.glob("/Users/aht/Documents/autocyber/13Prius/predict_data/add/YawRate/*.csv")
print(fs[0])
df = pd.read_csv(fs[0])
df.columns = ['Timestamp', 'Label', 'CarSpeed', 'SteeringAngle', 'YawRate', 'Gx', 'Gy']

results = graph.predict({"df": df})
results.keys()

And we should see that starting we can detect attacks starting at Timestamp 604.3105000000011

[x for x in results["event_detection_results"] if x["WindowInAttack"]][:5]

### 3e. Adding a message classifier, harmonizing human + ML models in the graph

For message-level classification we can simply bring back our gradient-boosted trees which did a decent job of recognizing injection messages. (Integrating sequence model such as Bidirectional LSTM is left as an exercise for the reader).

For convenient, we've re-orgarnized it as a H1st.Model, ready for use. The content of `models/gradient_boosting_msg_classifier.py` looks like this.

FEATURES = SENSORS + ["%s_TimeDiff" % s for s in SENSORS]

class GradientBoostingMsgClassifierModel(h1.Model):
    def load_data(self, num_samples=None):
        return util.load_data_daic(num_samples, shuffle=True)

    def prep_data(self, data):
        # concat multiple files into separate training/test pd.DataFrame
        def concat_processed_files(files):
            dfs = []
            for f in files:
                z = pd.read_csv(f)
                z.columns = ['Timestamp', 'Label', 'CarSpeed', 'SteeringAngle', 'YawRate', 'Gx', 'Gy',]
                z = util.compute_timediff_fillna(z)
                dfs.append(z)
            df2 = pd.concat(dfs)
            return df2
        return {
            "train_attack_df": concat_processed_files(data["train_attack_files"]),
            "test_attack_df": concat_processed_files(data["test_attack_files"])
        }

    def train(self, prepared_data):
        df = prepared_data["train_attack_df"]
        from sklearn.experimental import enable_hist_gradient_boosting
        from sklearn.ensemble import HistGradientBoostingClassifier
        X = df[FEATURES]
        y = df.Label == "Tx"
        self.model = HistGradientBoostingClassifier(max_iter=500).fit(X, y)

    def evaluate(self, data):        
        df = prepared_data["test_attack_df"]
        ypred = self.model.predict(df[FEATURES])
        import sklearn.metrics
        cf = sklearn.metrics.confusion_matrix(df.Label == "Tx", ypred)
        acc = sklearn.metrics.accuracy_score(df.Label == "Tx", ypred)
        print(cf)
        print("Accuracy = %.4f" % acc)
        self.metrics = {"confusion_matrix": cf, "accuracy": acc}
    
    def predict(self, data):
        df = data["df"].copy()
        df = util.compute_timediff_fillna(df)
        df['MsgIsAttack'] = 0
        df['WindowInAttack'] = 0
        for event_result in data["event_detection_results"]:
            if event_result['WindowInAttack']:
                # print("window %s in attack: event_result = %s" % (event_result['window_start'], event_result))
                in_window = (df.Timestamp >= event_result['window_start']) & (df.Timestamp < event_result['window_start'] + WINDOW_SIZE)
                w_df = df[in_window]
                ypred = self.model.predict(w_df[FEATURES])
                df.loc[in_window, "WindowInAttack"] = 1
                df.loc[in_window, "MsgIsAttack"] = ypred.astype(int)
                return {"injection_window_results": df}

from AutomotiveCybersecurity.models.gradient_boosting_msg_classifier import GradientBoostingMsgClassifierModel

m2 = GradientBoostingMsgClassifierModel()
data = m2.load_data(num_files=50)

prepared_data = m2.prep_data(data)

m2.train(prepared_data)

m2.evaluate(prepared_data)

m2.persist()

class NoOp(h1.Action):
    def call(self, command, inputs):
        pass

graph = h1.Graph()
graph.start()\
     .add(WindowGenerator())\
     .add(h1.Decision(MsgFreqEventDetectorModel().load(), decision_field="WindowInAttack"))\
     .add(yes=GradientBoostingMsgClassifierModel().load(),
          no=NoOp())
graph.end()

results = graph.predict({"df": df})
results.keys()

Now let's evaluate the whole graph, especially focusing on the event-level TPR & FPR since they are crucial in the safe-mode deployment use case.

from AutomotiveCybersecurity.util import evaluate_event_graph

evaluate_event_graph(graph, data['test_attack_files'])

Woa! We ran through all 400ms windows in the test samples and got event-level FPR=0.0% with zero false positives! (Note that this is still a subsample of the data, but once you've tried it on the full dataset the results should be the same: zero false positive at event-level.)

The message-level accuracy should be nearly the same because we used the same classifier. However the decomposition leads to separation of concerns and requirement for these two use cases. We're much more comfortable with the solution now both in terms of accuracy as well as robustness and explainability.

Another significance worth pointing out here is that we get multiple output streams from H1st.Graph: event-level outputs and msg-level outputs, exactly what we need for two different use cases we highlighted: safe-mode triggering and post-mortem analysis.

## Summary & Further Resources

That was a long tutorial! But not a trivial

To recap, the H1ST.AI principles & ideas we've learned:
  * Leverage use-case analysis to decompose problems and adopt different models at the right level of abstractions
  * Encoding human experience as a model
  * Combine human experience and data-driven insights to work harmoniously in a H1st Graph

Most importantly, we have used H1ST.AI to tackle a real-world challenging automotive cybersecurity problem, for which attack event labels are not available to start with, hence solving the Cold Start problem. 

It is important to stress that this is still a toy example IDS and much more is needed to handle attacks (e.g. replacement attacks where a whole ECU can be compromised & normal messages silenced and there won’t be a zig-zag pattern) and of course on-device vs cloud deployment, OTA updates, etc. But it is clear adopting H1ST.AI makes the problem much more tractable and explainable.

H1ST.AI framework further provides productivity tools for a team of Data Scientists and domain experts to collaborate on such complex software projects. Especially, we’ve seen our own productivity vastly when moving from a spaghetti code jungle of ML to a more principled H1ST project structure and make use of H1ST Model API & repository as well as Graph.

Interested? For further resources:
  * Check out our documentation site!
  * Contribute! Star/fork our Github repo, we're looking forward to your contribution to move real-world industrial AI head and to drive "industrial processes and machines and robots"!