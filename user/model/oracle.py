from h1st import Graph

import __init__
from h1st.h1flow.h1flow import Graph


class MyOracle(Graph):
    def __init__(self, k_model, k_gen, ensemble):
        super().__init__()
        self.start()
        self.add([k_model, k_gen])
        self.add(ensemble)
        self.end()
