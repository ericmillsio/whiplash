from decimal import Decimal

import numpy as np
from numpy.linalg import norm


def cosine_similarity_bulk(vector1, vectors_list, k=1):
    distances = norm(np.array(vectors_list) - np.array(vector1), axis=1)
    closest_indices = np.argsort(distances)[:k]
    return closest_indices


def cosine_similarity(vec1, vec2) -> float:
    norm1 = norm(vec1)
    norm2 = norm(vec2)
    if norm1 == 0 and norm2 == 0:
        return 1
    if norm1 == 0 or norm2 == 0:
        return 0
    return float(np.dot(vec1, vec2) / (norm1 * norm2))
