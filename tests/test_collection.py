import numpy as np
from moto import mock_dynamodb

from whiplash import Vector
from whiplash.whiplash import Whiplash


# Helper function to create a random vector
def create_random_vector(n_features, id="test_id"):
    return Vector(id=id, vector=np.random.rand(n_features))


def create_collection(n_features, n_planes):
    whiplash = Whiplash("us-west-1", "dev")
    whiplash.setup()
    return whiplash.create_collection(
        "test_collection",
        n_features=n_features,
        n_planes=n_planes,
        bit_start=8,
        bit_scale_factor=2,
    )


@mock_dynamodb
def test_insert_and_search():
    n_features = 10
    n_planes = 3
    collection = create_collection(n_features, n_planes)

    # Insert a vector
    vector = create_random_vector(n_features)
    collection.insert(vector)

    # Ensure the vector is inserted
    assert collection.get_item(vector.id).id == vector.id

    # Search for the inserted vector
    result = collection.search(vector.vector, k=5)

    # Ensure the searched vector is in the result
    print(result)
    assert any(item.id == vector.id for item in result)


@mock_dynamodb
def test_get_bulk_items():
    n_features = 10
    n_planes = 3
    collection = create_collection(n_features, n_planes)

    # Insert some vectors
    vectors = [create_random_vector(n_features, str(i)) for i in range(10)]
    for vector in vectors:
        collection.insert(vector)

    # Get the bulk items
    ids = [vector.id for vector in vectors]
    bulk_items = collection.get_bulk_items(ids)

    # Ensure the retrieved bulk items are correct
    assert len(bulk_items) == len(vectors)
    assert all(item.id in ids for item in bulk_items)


@mock_dynamodb
def test_insert_duplicates():
    n_features = 10
    n_planes = 3
    collection = create_collection(n_features, n_planes)

    # Insert a vector
    vector = create_random_vector(n_features)
    collection.insert(vector)
    collection.insert(vector)

    result = collection.search(vector.vector, k=5)

    # Ensure the vector is inserted only once
    assert len(result) == 1


@mock_dynamodb
def test_search_with_empty_bucket():
    n_features = 10
    n_planes = 3
    collection = create_collection(n_features, n_planes)

    # Search with an empty index
    vector = create_random_vector(n_features)
    result = collection.search(vector.vector, k=5)

    # Ensure the result is empty
    assert len(result) == 0


@mock_dynamodb
def test_search_with_small_k():
    n_features = 10
    n_planes = 3
    collection = create_collection(n_features, n_planes)

    # Insert some vectors
    vectors = [create_random_vector(n_features, str(i)) for i in range(5)]
    for vector in vectors:
        collection.insert(vector)

    # Search with k=1
    vector = create_random_vector(n_features)
    result = collection.search(vector.vector, k=1)

    # Ensure the result has only one item
    assert len(result) == 1
