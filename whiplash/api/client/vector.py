from dataclasses import dataclass


@dataclass
class Vector:
    id: str
    vector: list[float]

    def to_dict(self):
        return {"id": self.id, "vector": self.vector}

    @staticmethod
    def from_dict(item):
        return Vector(item["id"], item["vector"])


@dataclass
class CompVector:
    id: str
    vector: list[float]
    dist: float

    def __repr__(self) -> str:
        return f"{self.id}: {round(self.dist, 4)}"

    @staticmethod
    def from_dict(item):
        return CompVector(item["id"], item["vector"], item["dist"])
