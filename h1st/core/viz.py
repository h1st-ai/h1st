import os
from math import inf
from types import SimpleNamespace
from graphviz import Digraph, ExecutableNotFound, Graph
from h1st.h1flow.h1step import Decision

__theme__ = {
    'arrow_size': '0.5',
    'default_shape': 'rectangle',
    'default_style': 'rounded, filled',
    'edge_color': '#607894',
    'fill_color': '#7890AC',
    'font_name': 'helvetica',
    'font_size': '9',
    'text_color': '#7890AC',
}

theme = SimpleNamespace(**__theme__)

class DotGraphVisualizer:
    def __init__(self, graph: 'Graph'):
        self.graph = graph
        self.dot_graph = Digraph()
        self.visitor = GraphVisitor()
        self.nodes = []
        self.edges = []
        self._subgraphs = {}

    def render_dot_nodes(self):
        for rank, n in enumerate(self.graph.nodes.__dict__.values(), start=1):

            if n.rank is None:
                n.rank = str(rank)

            new_node = self.render_dot_node(n)
            self.nodes.append(new_node)
            self.clusterize_node(new_node)

            #special handling for Decision node
            edge_constraint = 'true'
            compass_point = None

            if isinstance(n, Decision):
                edge_constraint = 'false'
                compass_point = 'nw'
            else:
                edge_constraint = 'true'
                compass_point = None

            # '''point to end if no outgoing node is available'''
            # if len(n.edges) == 0:
            #     self.edges.append({
            #         'from': new_node['name'],
            #         'to': 'end', 'label': '',
            #         'constraint': edge_constraint,
            #         'compass_point': compass_point,
            #     })

            #connect edges
            seen = set()
            for ns in n.edges:
                if ns[0].rank is None:
                    ns[0].rank = str(rank + 1)

                connected_node = self.render_dot_node(ns[0])

                # self.nodes.append(connected_node)

                if (new_node['name'], connected_node['name']) in seen:
                    continue

                seen.add((new_node['name'], connected_node['name']))
                seen.add((connected_node['name'], new_node['name']))

                self.clusterize_node(connected_node)

                self.edges.append({
                    'from': new_node['name'], 
                    'to': connected_node['name'],
                    'label': ns[1],
                    'constraint': edge_constraint,
                    'compass_point': compass_point
                })

    def clusterize_node(self, node):
        if self._subgraphs.get(node['rank']) is None:
            self._subgraphs[node['rank']] = []

        self._subgraphs[node['rank']].append(node)

    def render_dot_node(self, node):
        return node.to_dot_node(self.visitor)

    def to_dot(self):
        self.dot_graph = Digraph()
        self.visitor = GraphVisitor()
        self.nodes = []
        self.edges = []
        self._subgraphs = {}

        mg = self.dot_graph

        mg.attr(
            'graph',
            compound='True',
            fontname=theme.font_name,
            fontsize=theme.font_size,
            splines="ortho",
            rankdir="LR"
        )

        mg.attr('node',
            color=theme.text_color,
            fillcolor=theme.fill_color,
            fontname=theme.font_name,
            fontsize=theme.font_size,
            shape=theme.default_shape,
            style=theme.default_style
        )

        mg.attr('edge',
            color=theme.edge_color,
            arrowsize=theme.arrow_size,
            fontname=theme.font_name,
            fontsize=theme.font_size,
            rank='same'
        )

        # mg.node(name='start', label='Start', shape='circle')

        self.render_dot_nodes()

        for i, rank in enumerate(self._subgraphs):
            cluster = self._subgraphs[rank]

            with mg.subgraph() as sg:
                sg.attr(rank='same')

                for subnode in cluster:
                    sg.node(**subnode)

        # for node in self.nodes:
        #     print(node)
        #     mg.node(**node)

        seen = set()  # XXX
        for edge in self.edges:
            if (edge['from'], edge['to']) in seen:
                continue

            seen.add((edge['from'], edge['to']))
            seen.add((edge['to'], edge['from']))

            mg.edge(
                edge['from'], edge['to'],
                label=edge['label']
            )

        mg.node(self.nodes[0]['name'], shape='circle')
        mg.node(self.nodes[-1]['name'], shape='circle')
        # mg.edge('start', self.nodes[0]['name'])

        # mg.subgraph(g)
        return mg

    def render_topology(self, target_file):
        dot = self.to_dot()

        try:
            basename = os.path.basename(target_file)

            if "." in basename:
                bits = basename.split(".")

                ext = bits[-1]
                basename = ".".join(bits[:-1])
            else:
                ext = "png"

            dot.render(
                filename=basename,
                format=ext,
                directory=os.path.dirname(target_file),
                cleanup=True,
            )
        except ExecutableNotFound:
            raise EngineNotAvailableException()

        return dot


    def _repr_svg_(self):
        dot = self.to_dot()
        return dot.pipe(format='svg').decode('utf8')


class EngineNotAvailableException(Exception):
    pass


class GraphVisitor:
    def render_node_label(self, node, extra_label=""):
        # print(node.callable)
        # print(type(node.callable).__name__)
        # return "{}\n {}".format(type(node).__name__, node.id)
        return node.id

    def render_node_name(self, node):
        return "{}\n {}".format(type(node).__name__, id(node))

    def render_dot_decision_node(self, node):
        label = self.render_node_label(node)
        node_name = self.render_node_name(node)
        return dict(name=node_name, label=label, shape="diamond", style="filled", rank=node.rank)

    def render_dot_action_node(self, node):
        label = self.render_node_label(node)
        node_name = self.render_node_name(node)
        return dict(name=node_name, label=label, shape="rectangle", rank=node.rank)
