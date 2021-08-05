from unittest import TestCase
from h1st.h1flow.h1flow import Graph
from h1st.h1flow.h1step import Action, Decision
from h1st.model.ml_model import MLModel


class GraphVizTestCase(TestCase):
    def test_render_graph(self):
        class DummyModel(MLModel):
            pass

        g = Graph()
        g.start()

        g.add(DummyModel(), id='m1')\
            .add(Decision(DummyModel(), id='m2'))\
            .add(
                yes=Action(DummyModel(), id='m3'),
                no=Action(DummyModel(), id='m4'),
            )

        g.end()

        g.visualize().to_dot()
