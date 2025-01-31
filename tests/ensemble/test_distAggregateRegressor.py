import unittest
from river import preprocessing, linear_model, optim
from skmultiflow.data.hyper_plane_generator import HyperplaneGenerator
from sail.ensemble.distAggregateRegressor import DistAggregateRegressor
import numpy as np
from array import array
import ray
import warnings


class TestDistAggregateRegressor(unittest.TestCase):

    def setUp(self):
        warnings.simplefilter("ignore", ResourceWarning)

    def tearDown(self):
        warnings.simplefilter("default", ResourceWarning)

    @classmethod
    def setUpClass(cls):
        ray.init(local_mode=True)

    @classmethod
    def tearDownClass(cls):
        ray.shutdown()

    def test_dar(self):
        stream = HyperplaneGenerator(random_state=1)

        optimizers = [optim.SGD(0.01), optim.RMSProp(), optim.AdaGrad()]

        # prepare the ensemble
        learner = DistAggregateRegressor(
            estimators=[linear_model.LinearRegression(optimizer=o, intercept_lr=.1)
                                           for o in optimizers])
        cnt = 0
        max_samples = 50
        y_pred = array('f')
        X_batch = []
        y_batch = []
        wait_samples = 10

        while cnt < max_samples:
            X, y = stream.next_sample()
            X_batch.append(X[0])
            y_batch.append(y[0])
            # Test every n samples
            if (cnt % wait_samples == 0) and (cnt != 0):
                y_pred.append(learner.predict(X)[0])
            learner.partial_fit(X, y)
            cnt += 1
        expected_predictions = np.array([0.6342105269432068, 0.7355141639709473,
                                           0.09660783410072327, 0.25919777154922485])

        assert np.allclose(y_pred, expected_predictions)
        assert type(learner.predict(X)) == np.ndarray

        learner = DistAggregateRegressor(
            estimators=[linear_model.LinearRegression(optimizer=o, intercept_lr=.1)
                                           for o in optimizers], aggregator="windsor")
        cnt = 0
        max_samples = 50
        y_pred = array('f')
        X_batch = []
        y_batch = []
        wait_samples = 10

        while cnt < max_samples:
            X, y = stream.next_sample()
            X_batch.append(X[0])
            y_batch.append(y[0])
            # Test every n samples
            if (cnt % wait_samples == 0) and (cnt != 0):
                y_pred.append(learner.predict(X)[0])
            learner.partial_fit(X, y)
            cnt += 1
        expected_predictions = np.array([0.6946223378181458, 0.6883502006530762,
                                0.9850282073020935, 0.297251433134079])
        assert np.allclose(y_pred, expected_predictions)
        assert type(learner.predict(X)) == np.ndarray


if __name__ == '__main__':
    unittest.main()
