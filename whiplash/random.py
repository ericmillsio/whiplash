import numpy as np


def random_data(num_data_points=1000):
    # Example usage:
    n_features = 384

    # Generate random data points for testing
    return np.random.randn(num_data_points, n_features)
