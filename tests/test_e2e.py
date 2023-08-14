import time
import unittest

import numpy as np
from moto import mock_dynamodb

from whiplash import Vector, Whiplash


def create_random_vector(n_features, id="test_id"):
    return Vector(id=id, vector=np.random.rand(n_features))


class TestE2E(unittest.TestCase):
    @mock_dynamodb
    def setUp(self):
        # Initialize the Whiplash instance with mock DynamoDB
        self.region = "us-east-1"
        self.stage = "dev"
        self.project_name = "test_project"
        self.whiplash = Whiplash(
            self.region, self.stage, project_name=self.project_name
        )

    @mock_dynamodb
    def test_build(self):
        # Test getting collection info
        collection_name = "test_collection"
        n_features = 128
        n_planes = 10
        bit_start = 1
        bit_scale_factor = 0.5

        self.whiplash.setup()

        # Create a collection
        start_time = time.time()
        self.whiplash.create_collection(
            collection_name, n_features, n_planes, bit_start, bit_scale_factor
        )
        end_time = time.time()
        create_collection_time = end_time - start_time

        # Get the collection
        collection = self.whiplash.get_collection(collection_name)

        assert collection is not None

        for i in range(100):
            vector = create_random_vector(n_features, id=f"test_id_{i}")
            collection.insert(vector)

        # Measure the time taken to execute the search function
        start_time = time.time()
        query = create_random_vector(n_features)
        result = collection.search(query.vector, 10)
        assert len(result) == 10
        end_time = time.time()
        search_time = end_time - start_time

        # Measure the time taken to execute the insert function
        start_time = time.time()
        for i in range(100):
            vector = create_random_vector(n_features, id=f"test_id_{i + 100}")
            collection.insert(vector)
        end_time = time.time()
        insert_time = (end_time - start_time) / 100

        # Measure the time taken to execute the get_collection function
        start_time = time.time()
        self.whiplash.get_collection(collection_name)
        end_time = time.time()
        get_collection_time = end_time - start_time

        # Assert timing of the key functions
        assert (
            create_collection_time < 0.2
        ), "Create collection function took more than 0.2 seconds"
        assert search_time < 0.2, "Search function took more than 0.2 seconds"
        assert insert_time < 0.1, "Insert function took more than 0.1 second"
        assert (
            get_collection_time < 0.1
        ), "get_collection function took more than 0.1 seconds"


if __name__ == "__main__":
    unittest.main()
