import numpy as np

from pyelm import logger_pyelm
from .nelm import NELM
from pyelm.clf_utility.target_encode import *


class AdaBoostNELM(NELM):
    """
    AdaBoost meta algorithm applied to Neural Extreme Learning
    Machine.
    """
    weight = None
    alpha = None
    beta_ensemble = None

    def __init__(self):
        logger_pyelm.debug('AdaBoost Neural Extreme Learning Machine instanced')

    def fit(self, train, parameters):
        """
        Use some train (data and target) and parameters to fit the classifier and construct the rules.

        :type train: dict
        :param train: dictionary with two keys: 'data', with the features, and 'target' with an
            array of the labels.

        :type parameters: dict
        :param parameters: dictionary with the parameters needed for training. It must contain:
                - hidden_neurons: the number of the neurons in the hidden layer.
                - C: regularization of H matrix.
        :return:
        """
        self.t = train['target'].shape[1]
        self.hidden_neurons = parameters['hidden_neurons'] if parameters['hidden_neurons'] != 0 else self.t
        self.C = parameters['C']

        n = train['data'].shape[0]
        m = train['data'].shape[1]
        h = self.hidden_neurons

        self.input_weight = np.random.rand(h, m)  # h x m
        self.bias_vector = np.random.rand(h, 1)  # h x 1
        self.weight = np.ones(n) / n
        bias_matrix = np.resize(self.bias_vector.transpose(), (n, h)).transpose()
        temp_H = np.dot(self.input_weight, train['data'].transpose()) + bias_matrix  # h x n
        H = self.neuron_fun(temp_H.transpose())  # n x h
        self.beta_ensemble = []

        for s in range(self.ensemble_size):
            beta_s = self.fit_step(H=H, train_target=train['target'])
            self.beta_ensemble.append(beta_s)

    def fit_step(self, H, train_target):
        """

        :param H:
        :param s:
        :param train_target:
        :return:
        """
        weight_matrix = np.diag(self.weight)
        H_reg = np.eye(H.shape[1]) / self.C + np.dot(np.dot(H.transpose(), weight_matrix), H)
        beta_s = np.linalg.solve(H_reg, np.dot(np.dot(H.transpose(), weight_matrix), train_target))

        # Calculate errors
        y_hat = np.dot(H, beta_s)

        error_vector = (j_renorm(y_hat) == train_target).min(axis=1)
        e_s = (self.weight * error_vector).sum() / self.weight.sum()
        alpha_s = np.log((1 - e_s) / e_s) + np.log(beta_s.shape[1] - 1)
        self.weight = self.weight * np.exp(alpha_s * error_vector)
        self.weight = self.weight / self.weight.sum()  # Normalize
        return beta_s

    def predict(self, test_data):
        """
        Once instanced, classifier can predict test target from test data, using some mathematical
        rules.

        :param test_data:
        :return:
        """
        n = test_data.shape[0]  # Number of instances to classify
        # bias_matrix = np.resize(self.bias_vector, (self.hidden_neurons, n)).transpose()  # h x n
        bias_matrix = np.resize(self.bias_vector.transpose(), (n, self.hidden_neurons)).transpose()
        temp_H = np.dot(self.input_weight, test_data.transpose()) + bias_matrix  # h x n
        H = self.neuron_fun(temp_H.transpose())

        test_target = np.empty((n, self.t))
        for s in range(self.ensemble_size):
            beta_s = self.beta_ensemble[s]
            indicator = np.dot(H, beta_s)
            y_hat = j_renorm(indicator)
            test_target += y_hat

        test_target = j_renorm(test_target)
        return test_target