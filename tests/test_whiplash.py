import unittest

from moto import mock_dynamodb

from whiplash import Whiplash


class TestWhiplash(unittest.TestCase):
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
    def test_create_collection(self):
        # Test creating a collection
        collection_name = "test_collection"
        n_features = 128
        n_planes = 10
        bit_start = 1
        bit_scale_factor = 0.5

        self.whiplash.setup()

        collection = self.whiplash.create_collection(
            collection_name, n_features, n_planes, bit_start, bit_scale_factor
        )

        assert collection is not None

        # Check if the collection was correctly created in DynamoDB and S3
        loaded_collection = self.whiplash.get_collection(collection_name)

        assert loaded_collection is not None

        self.assertEqual(loaded_collection.config.n_features, n_features)
        self.assertEqual(loaded_collection.config.n_planes, n_planes)
        self.assertEqual(loaded_collection.config.bit_start, bit_start)
        self.assertEqual(loaded_collection.config.bit_scale_factor, bit_scale_factor)

    @mock_dynamodb
    def test_get_collection(self):
        # Test getting collection info
        collection_name = "test_collection"
        n_features = 128
        n_planes = 10
        bit_start = 1
        bit_scale_factor = 0.5

        self.whiplash.setup()

        # Create a collection
        self.whiplash.create_collection(
            collection_name, n_features, n_planes, bit_start, bit_scale_factor
        )

        # Get the collection
        collection = self.whiplash.get_collection(collection_name)

        assert collection is not None

        # Check if the collection was retrieved with the correct configuration
        self.assertEqual(
            collection.collection_id,
            f"{self.project_name}_{self.stage}_{collection_name}",
        )
        self.assertEqual(collection.config.name, collection_name)
        self.assertEqual(collection.config.region, self.region)
        self.assertEqual(collection.config.stage, self.stage)
        self.assertEqual(collection.config.project_name, self.project_name)
        self.assertEqual(collection.config.n_features, n_features)
        self.assertEqual(collection.config.n_planes, n_planes)
        self.assertEqual(collection.config.bit_start, bit_start)
        self.assertEqual(collection.config.bit_scale_factor, bit_scale_factor)


if __name__ == "__main__":
    unittest.main()
