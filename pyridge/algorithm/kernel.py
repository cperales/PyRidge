import numpy as np
from pyridge.utils.target_encode import j_renorm
from pyridge.generic import KernelMethod


class KRidge(KernelMethod):
    """
    Kernel Ridge classifier.
    """
    __name__ = 'Kernel Ridge classifier'

    def fit(self, train_data, train_target):
        self.t = train_target.shape[1]
        n = train_data.shape[0]
        # m = train_data.shape[1]
        self.train_data = train_data

        omega_train = self.kernel_fun(X=self.train_data)

        if self.C == 0:  # No regularization
            self.output_weight = np.linalg.solve(omega_train, train_target)
        else:
            alpha = omega_train * self.C + np.eye(n)
            self.output_weight = np.linalg.solve(alpha, train_target)

    def predict(self, test_data):
        """
        Once instanced, classifier can predict test target
        from test data, using some mathematical
        rules.

        :param numpy.array test_data: matrix of data to predict.
        :return: matrix of the predicted targets.
        """
        omega_test = self.kernel_fun(X=self.train_data, Y=test_data)
        indicator = np.dot(omega_test.T, self.output_weight)
        test_target = j_renorm(indicator)
        return test_target

    def get_params(self, deep=False):
        to_return = None
        to_return = {'C': self.C,
                     'k': self.k,
                     'kernel_fun': self.kernel_fun}
        if deep is True:
            to_return.update(self.__dict__)
        return to_return

    def set_params(self, parameters):
        """
        :type parameters: dict
        :param parameters: dictionary with the parameters needed
            for training. It must contain:

                - k: length scale of Radial Basis Function kernel
                - C: regularization.
        """
        self.C = parameters['C']
        self.k = parameters['k']
        self.kernel_fun = self.kernel(length_scale=self.k)

    def __call__(self, parameters):
        """
        :type parameters: dict
        :param parameters: dictionary with the parameters needed
            for training. It must contain:

                - k: length scale of Radial Basis Function kernel
                - C: regularization.
        """
        self.set_params(parameters)