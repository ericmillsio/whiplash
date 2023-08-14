import numpy as np


def vector_plane_hash(vector: np.ndarray, uniform_plane: np.ndarray) -> str:
    if vector is None or uniform_plane is None:
        raise TypeError("Input vector or uniform plane is None")

    projections: np.ndarray = np.dot(vector, uniform_plane)
    # Compute the hash code as 0 or 1 based on the sign of the projection
    hash_code: str = "".join((projections >= 0).astype(int).astype(str))

    if len(hash_code) == 0:
        raise ValueError("Hash key generated is empty")
    # Change the base of the hash code from 2 to 58
    return np.base_repr(int(hash_code, 2), 36)
