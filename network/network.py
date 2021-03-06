from keras import Sequential
from keras.layers import Dense
import numpy as np
import pandas as pd
import pickle
"""All code written by Yoav Kaliblotzky"""


def load_network(filename):
    """Loads a neural network from the specified file name

    :param filename: name of file to read
    :return: New neural network with weights and structure specified in file
    """
    temp = pickle.load(filename)
    n = Network(None, None, None, None, None, None, None)
    n.__setstate__(temp)
    return n


def evaluate_fitness(network, x, y):
    """Runs the model on the samples, and then checks how many it predicted
     correctly.

    :param network: network to check fitness of
    :param x: list or numpy array of lists with size = num_inputs
    :param y: list of the same size as x with the 0 or 1
    :return: float for percentage of results the model predicted correctly
    """
    if isinstance(x, type(pd.DataFrame())):
        if x.shape[1] != network.num_inputs:
            raise ValueError('Invalid number of inputs.')

        if isinstance(y, type(pd.DataFrame())) or isinstance(
                y, type(pd.Series())):
            if x.shape[0] != y.shape[0]:
                raise ValueError('Length of x and y differ.')
            if y.shape[1] != network.num_outputs:
                raise ValueError('Invalid number of outputs.')
        else:
            if x.shape[0] != len(y):
                raise ValueError('Length of x and y differ.')
            if len(y[0]) != network.num_outputs:
                raise ValueError('Invalid number of outputs.')
    else:
        try:
            if len(x) != len(y):
                raise ValueError('Length of x and y differ.')
            elif len(x[0]) != network.num_inputs:
                raise ValueError('Invalid number of inputs.')
            elif len(y[0]) != network.num_outputs:
                raise ValueError('Invalid number of outputs.')
        except TypeError:
            raise ValueError('Expected input with shape [n, num_inputs]')

        if not isinstance(x, type(np.array([1]))):
            x = np.array(x)

    if network.num_outputs == 1:
        preds = network.model.predict(x)
        predictions = [int(preds[i][0]+.5) for i in range(len(preds))]
        network.fitness = FitnessValue(sum([1 if predictions[i] == y['result'][i] else
                                            0 for i in range(y.shape[0])]) / len(y))
        return network.fitness.values


class Network:
    """Wrapper class for keras neural networks

    """

    def __init__(self, num_layers, num_inputs, num_neurons, num_outputs,
                 activations, nid):
        """Initialize network.

        :param num_layers: number of layers
        :param num_inputs: number of inputs
        :param num_neurons: (list) number of neurons in each layer
        :param num_outputs: number of outputs
        :param activations: (list) activation functions for each layer
        """
        if not (num_neurons or num_outputs or num_inputs or num_layers):
            pass
        else:
            if num_layers < 2:
                raise ValueError('Invalid number of layers (must be ≥ 2')
            self.num_layers = num_layers
            self.num_inputs = num_inputs
            self.num_neurons = num_neurons
            self.num_outputs = num_outputs
            self.activations = activations

            self.model = Sequential()
            self.model.add(Dense(num_neurons, input_dim=num_inputs,
                           activation=activations[0]))

            [self.model.add(Dense(num_neurons, activation=activations[i + 1]))
             for i in range(self.num_layers - 2)]

            self.model.add(Dense(num_outputs, activation=activations[-1]))
            self.id = nid
            self.fitness = FitnessValue(0)

    def set_weights(self, layer_number, weights):
        """Sets the weights for the specified layers to the specified weights.

        :param layer_number: list of layers you want to set weights for
        :param weights: list of
        :return: None
        """
        if len(weights) != len(self.get_weights(layer_number)) or \
                len(weights[0]) != len(self.get_weights(layer_number)[0]):
            raise ValueError('Invalid size of weights list')

        temp_weights = self.model.layers[layer_number].get_weights()
        temp_weights[0] = weights
        self.model.layers[layer_number].set_weights(temp_weights)

    def get_weights(self, layer):
        """Returns the weights for a given layer

        :rtype: object
        :param layer: layer to get weights for
        :return: numpy array of weights of the specified layer
        """
        if layer < 0 or layer >= self.num_layers:
            raise IndexError('Invalid layer number')

        return self.model.layers[layer].get_weights()[0]

    def write_to_file(self, filename=None):
        """
        Writes all of the data from the network into a file
        :return: none
        """
        if not filename:
            filename = 'network{}'.format(self.id)
        data = self.__getstate__()

        pickle.dump(data, filename)


    def predict(self, x):
        """Returns prediction values for each of the inputs

        :param x: list or numpy array of lists with size = num_inputs
        :return: list of size = len(x) of lists with size = num_outputs
        """
        if isinstance(x, type(pd.DataFrame())):
            if x.shape[1] != self.num_inputs:
                raise ValueError('Invalid number of inputs.')
        else:
            try:
                if len(x[0]) != self.num_inputs:
                    raise ValueError('Invalid number of inputs.')
            except TypeError:
                raise ValueError('Expected input with shape [n, num_inputs]')
            if not isinstance(x, type(np.array([1]))):
                x = np.array(x)
        return self.model.predict(x)

    def __getstate__(self):
        selfdict = dict()
        selfdict['num_layers'] = self.num_layers
        selfdict['num_inputs'] = self.num_inputs
        selfdict['num_neurons'] = self.num_neurons
        selfdict['num_outputs'] = self.num_outputs
        selfdict['activations'] = self.activations
        selfdict['id'] = self.id
        try:
            selfdict['fitness'] = self.fitness.values
        except AttributeError:
            selfdict['fitness'] = FitnessValue(0)

        selfdict['weights'] = []
        for layer in range(self.num_layers):
            selfdict['weights'].append(self.get_weights(layer))

        return selfdict

    def __setstate__(self, state):
        state['model'] = Sequential()
        state['model'].add(Dense(state['num_neurons'],
                                 input_dim=state['num_inputs'],
                                 activation=state['activations'][0]))

        [state['model'].add(Dense(state['num_neurons'],
                                  activation=state['activations'][i + 1]))
         for i in range(state['num_layers'] - 2)]

        state['model'].add(Dense(state['num_outputs'],
                                 activation=state['activations'][-1]))
        state['fitness'] = FitnessValue(state['fitness'])

        for layer in range(state['num_layers']):
            temp = state['model'].layers[layer].get_weights()
            temp[0] = state['weights'][layer]
            state['model'].layers[layer].set_weights(temp)

        self.__dict__.update(state)

    # Getter methods for attributes
    def get_num_layers(self):
        return self.num_layers

    def get_num_inputs(self):
        return self.num_inputs

    def get_num_outputs(self):
        return self.num_outputs

    def get_num_neurons(self):
        return self.num_neurons

    def get_network_id(self):
        return self.id


class FitnessValue:
    def __init__(self, value):
        if isinstance(value, FitnessValue):
            self.values = value.values
        else:
            self.values = value

        self.valid = True if 1 >= self.values >= 0 else False

    def __eq__(self, other):
        try:
            self.values
        except AttributeError:
            self.values = 0
        try:
            other.values
        except AttributeError:
            other = FitnessValue(0)
        return self.values == other.values

    def __gt__(self, other):
        try:
            self.values
        except AttributeError:
            self.values = 0
        try:
            other.values
        except AttributeError:
            other = FitnessValue(0)
        return self.values > other.values

    def __lt__(self, other):
        try:
            self.values
        except AttributeError:
            self.values = 0
        try:
            other.values
        except AttributeError:
            other = FitnessValue(0)
        return self.values < other.values
