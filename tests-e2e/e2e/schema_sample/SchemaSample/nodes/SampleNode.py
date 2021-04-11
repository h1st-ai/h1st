import h1st.core as h1


class SampleNode(h1.Action):
    def call(self, command, inputs):
        return 'sample node'
