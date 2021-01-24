import h1st.core as h1

import config
import utils
from msg_freq_event_detector import MsgFreqEventDetectorModel
from gradient_boosting_msg_classifier import GradientBoostingMsgClassifierModel


class WindowGenerator(h1.Action):
    def call(self, command, inputs):
        window_starts = [w for w in utils.gen_windows(inputs['df'], window_size=config.WINDOW_SIZE, step_size=config.WINDOW_SIZE)]
        return {'window_starts': window_starts}

class NoOp(h1.Action):
    def call(self, command, inputs):
        pass

def create_autocyber_graph():
    graph = h1.Graph()
    graph.start()\
        .add(WindowGenerator())\
        .add(h1.Decision(MsgFreqEventDetectorModel().load(), decision_field="WindowInAttack"))\
        .add(yes=GradientBoostingMsgClassifierModel().load(),
            no=NoOp())
    graph.end()
    return graph