import h1st as h1
from .models.abc import AbcModel


class AbcGraph(h1.Graph):
    def __init__(self):
        super().__init__()

        self.start()
        self.add(AbcModel())
        self.end()
