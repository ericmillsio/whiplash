import numpy as np
import pytest
from whiplash.vector_math import cosine_similarity, cosine_similarity_bulk


def test_cosine_similarity_bulk():
    # Test with two random vectors and k=1
    vector1 = np.array([1.0, 2.0, 3.0])
    vector2 = np.array([4.0, 5.0, 6.0])
    vectors_list = [np.array([7.0, 8.0, 9.0]), np.array([10.0, 11.0, 12.0])]
    result = cosine_similarity_bulk(vector1, vectors_list, k=1)

    # Ensure the result has only one closest index
    assert len(result) == 1


def test_cosine_similarity_orthogonal():
    # Test with two orthogonal vectors
    vec1 = np.array([1.0, 0.0, 0.0])
    vec2 = np.array([0.0, 1.0, 0.0])
    similarity = cosine_similarity(vec1, vec2)

    similarity_list = cosine_similarity_bulk(vec1, [vec2], k=1)

    # Ensure the similarity is 0 (orthogonal vectors)
    assert similarity_list[0] == similarity
    assert similarity == pytest.approx(0.0, abs=1e-6)


def test_cosine_similarity_identical():
    # Test with two identical vectors
    vec3 = np.array([2.0, 3.0, 4.0])
    similarity = cosine_similarity(vec3, vec3)

    # Ensure the similarity is 1 (identical vectors)
    assert similarity == pytest.approx(1.0, abs=1e-6)


def test_cosine_similarity_with_zero_vector():
    # Test with one zero vector and one non-zero vector
    zero_vector = np.zeros(3)
    non_zero_vector = np.array([1.0, 2.0, 3.0])
    similarity = cosine_similarity(zero_vector, non_zero_vector)

    # Ensure the similarity is 0 (one zero vector)
    assert similarity == pytest.approx(0.0, abs=1e-6)


def test_cosine_similarity_with_zero_norm():
    # Test with vectors of zero norm (result should be 0)
    vec1 = np.array([1.0, 2.0, 3.0])
    vec2 = np.zeros(3)
    similarity = cosine_similarity(vec1, vec2)

    # Ensure the similarity is 0 (one zero vector)
    assert similarity == pytest.approx(0.0, abs=1e-6)

    # Test with two zero vectors (result should be 1)
    vec3 = np.zeros(3)
    similarity = cosine_similarity(vec3, vec2)

    # Ensure the similarity is 1 (two zero vectors)
    assert similarity == pytest.approx(1.0, abs=1e-6)
