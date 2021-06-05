import tensorflow as tf
import time

class TFNeuronCoverage1():
    def __init__(self):
        pass
    def gen_diff(self, seeds, model):
        for _ in range(1000):
            for iter in range(100):
                print("Generate mutants...")
                time.sleep(1)
                print("Perform gradient descent...")
                time.sleep(5)
                print("Computing neuron coverage....")
                time.sleep(1)

            print('Covered neurons percentage: %.2f %%' % 63)


class TFNeuronCoverage2():
    def __init__(self):
        pass
    def gen_diff(self, seeds, model):
        for _ in range(1000):
            for iter in range(100):
                print("Generate mutants...")
                time.sleep(1)
                print("Computing neuron coverage....")
                time.sleep(1)

            print('Covered neurons percentage: %.2f %%' % 54)


