from dataclasses import dataclass
from decimal import Decimal

import numpy as np


def plane_to_bit_count(bit_start: int, bit_scale_factor: float, plane_id: int) -> int:
    """Compute the number of bits for a given plane"""
    return int(bit_start + plane_id * bit_scale_factor)


@dataclass
class CollectionConfig:
    """Configuration for a collection"""

    name: str
    region: str
    stage: str
    project_name: str
    n_features: int
    n_planes: int
    bit_start: int
    bit_scale_factor: float
    uniform_planes: (dict[int, np.ndarray] | None) = None

    @property
    def id(self) -> str:
        return f"{self.project_name}_{self.stage}_{self.name}"

    def __repr__(self) -> str:
        return f"CollectionConfig(n_features={self.n_features}, n_planes={self.n_planes}, bit_start={self.bit_start}, bit_scale_factor={self.bit_scale_factor})"

    def create_uniform_planes(self):
        """Create a set of random hyperplanes"""
        if self.uniform_planes:
            return
        self.uniform_planes = {}
        for plane_id in range(self.n_planes):
            self.uniform_planes[plane_id] = np.random.randn(
                plane_to_bit_count(self.bit_start, self.bit_scale_factor, plane_id),
                self.n_features,
            ).T

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "region": self.region,
            "stage": self.stage,
            "project_name": self.project_name,
            "n_features": self.n_features,
            "n_planes": self.n_planes,
            "bit_start": self.bit_start,
            "bit_scale_factor": self.bit_scale_factor,
        }

    def to_dynamo(self):
        if not self.uniform_planes:
            raise ValueError(
                "Uniform planes must be created before writing to DynamoDB"
            )
        return {
            "id": self.id,
            "name": self.name,
            "region": self.region,
            "stage": self.stage,
            "project_name": self.project_name,
            "n_features": self.n_features,
            "n_planes": self.n_planes,
            "bit_start": self.bit_start,
            "bit_scale_factor": Decimal(self.bit_scale_factor),
            "uniform_planes": {
                str(plane_id): plane.tobytes()
                for plane_id, plane in self.uniform_planes.items()
            },
        }

    @staticmethod
    def from_dict(config: dict):
        return CollectionConfig(
            config["name"],
            config["region"],
            config["stage"],
            config["project_name"],
            config["n_features"],
            config["n_planes"],
            config["bit_start"],
            config["bit_scale_factor"],
            {
                int(plane_id): np.frombuffer(plane, dtype=float).reshape(
                    (
                        config["n_features"],
                        plane_to_bit_count(
                            int(config["bit_start"]),
                            float(config["bit_scale_factor"]),
                            int(plane_id),
                        ),
                    )
                )
                for plane_id, plane in config["uniform_planes"].items()
            }
            if "uniform_planes" in config
            else None,
        )
