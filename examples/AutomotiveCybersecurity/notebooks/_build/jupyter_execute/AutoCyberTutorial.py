## NOTE: execution of this notebook requires private access to the dataset. We're making the data available soon.  In the mean time, hang on tight!

import h1st as h1
h1.init()

import pandas as pd
import numpy as np
import sklearn.metrics


from AutomotiveCybersecurity.models.msg_freq_event_detector import MsgFreqEventDetectorModel
m = MsgFreqEventDetectorModel()
data = m.load_data(num_files=5)

m.train(data)

m.stats

# Don't run automatically this easily overwite latest version in AHT's computer, 
# I need to use correct version in the tutorial notebooks
# m.persist()

from AutomotiveCybersecurity.graph import WindowGenerator

df = pd.read_csv(data["test_attack_files"][0])
df.columns = ['Timestamp', 'Label', 'CarSpeed', 'SteeringAngle', 'YawRate', 'Gx', 'Gy']

graph = h1.Graph()
graph.start()\
     .add(WindowGenerator())\
     .add(m)
graph.end()
results = graph.predict({"df": df})

results["event_detection_results"]

from AutomotiveCybersecurity.models.gradient_boosting_msg_classifier import GradientBoostingMsgClassifierModel

m2 = GradientBoostingMsgClassifierModel()
data = m2.load_data(20)
prepared_data = m2.prep_data(data)

m2.train(prepared_data)

# Don't run automatically this easily overwite latest version in AHT's computer, 
# I need to use correct version in the tutorial notebooks
# m2.persist()

m2.evaluate(prepared_data)

m2.metrics['confusion_matrix']

from AutomotiveCybersecurity.graph import WindowGenerator

class NoOp(h1.Action):
    def call(self, command, inputs):
        pass

graph = h1.Graph()
graph.start()\
     .add(WindowGenerator())\
     .add(h1.Decision(m, decision_field="WindowInAttack"))\
     .add(yes=m2,
          no=NoOp())
graph.end()

df = pd.read_csv(data['test_attack_files'][0])
df.columns = ['Timestamp', 'Label', 'CarSpeed', 'SteeringAngle', 'YawRate', 'Gx', 'Gy',]

results = graph.predict({"df": df})

print(sklearn.metrics.confusion_matrix(results['injection_window_results']["Label"] == "Tx", 
                                       results['injection_window_results']["MsgIsAttack"]))
print(sklearn.metrics.accuracy_score(results['injection_window_results']["Label"] == "Tx", 
                                       results['injection_window_results']["MsgIsAttack"]))

att_wins = len([x for x in results["event_detection_results"] if x["WindowInAttack"]])
att_wins

assert len(results) > 0

from AutomotiveCybersecurity.util import evaluate_event_graph

evaluate_event_graph(graph, data['test_attack_files'])

