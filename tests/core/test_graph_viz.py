from unittest import TestCase
from h1st.core import Graph, Decision, Action, Model


class GraphVizTestCase(TestCase):
    def test_render_graph(self):
        class DummyModel(Model):
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
