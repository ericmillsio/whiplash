from dataclasses import dataclass

import numpy as np


@dataclass
class Vector:
    id: str
    vector: np.ndarray

    def to_dict(self):
        return {"id": self.id, "vector": self.vector.tolist()}

    def to_dynamo(self):
        return {"id": self.id, "vector": self.vector.astype(np.float32).tobytes()}

    @staticmethod
    def from_dynamo(item):
        return Vector(
            item["id"], np.array(np.frombuffer(item["vector"], dtype=np.float32))
        )


@dataclass
class CompVector:
    id: str
    vector: np.ndarray
    dist: float

    def to_dict(self):
        return {"id": self.id, "vector": self.vector.tolist(), "dist": self.dist}

    def __repr__(self) -> str:
        return f"{self.id}: {round(self.dist, 4)}"
