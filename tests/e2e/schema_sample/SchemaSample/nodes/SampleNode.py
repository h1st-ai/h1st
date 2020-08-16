import h1st as h1


class SampleNode(h1.Action):
    def call(self, command, inputs):
        return 'sample node'
