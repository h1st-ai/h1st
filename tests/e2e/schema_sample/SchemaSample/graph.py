import h1st.core as h1
from .nodes.SampleNode import SampleNode
from .models.SchemaSample import SchemaSampleModel

class SchemaSampleGraph(h1.Graph):
    def __init__(self):
        super().__init__()

        self.start()
        self.add(SampleNode())
        self.add(SchemaSampleModel())
        self.end()
