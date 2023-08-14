import numpy as np
import pytest

from whiplash.hashing import vector_plane_hash

np.random.seed(42)


def create_uniform_planes(size) -> np.ndarray:
    return np.random.randn(8, size).T


def test_vector_plane_hash_with_zeros():
    hash_code_zeros = np.zeros(10, dtype=np.float64)
    key_zeros = vector_plane_hash(hash_code_zeros, create_uniform_planes(10))
    assert key_zeros == "73"


def test_vector_plane_hash_with_ones():
    hash_code_ones = np.ones(10, dtype=np.float64)
    key_ones = vector_plane_hash(hash_code_ones, create_uniform_planes(10))
    assert key_ones == "48"


def test_vector_plane_hash_with_different_sizes():
    hash_code_size_1 = np.array([1], dtype=np.uint8)
    assert vector_plane_hash(hash_code_size_1, create_uniform_planes(1)) == "24"

    hash_code_size_100 = np.random.rand(100).astype(np.uint8)
    assert vector_plane_hash(hash_code_size_100, create_uniform_planes(100)) == "73"


def test_vector_plane_hash_with_invalid_input():
    with pytest.raises(TypeError):
        vector_plane_hash(None, np.random.rand(10))

    hash_code_empty = np.array([], dtype=np.uint8)
    with pytest.raises(ValueError):
        vector_plane_hash(hash_code_empty, np.random.rand(10))


def test_vector_plane_hash_with_empty_input():
    hash_code_empty = np.array([], dtype=np.uint8)
    with pytest.raises(ValueError):
        vector_plane_hash(hash_code_empty, np.random.rand(10))
