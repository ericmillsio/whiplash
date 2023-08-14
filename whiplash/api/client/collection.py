import logging

import numpy as np

from whiplash.api.client.api_config import APIConfig
from whiplash.api.client.vector import CompVector, Vector

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Collection:
    """A collection of vectors with LSH indexing and retrieval"""

    api: APIConfig
    name: str
    project_name: str
    metadata: dict

    def __init__(
        self,
        api: APIConfig,
        name: str,
        project_name: str,
        metadata: dict = {},
    ):
        self.api = api
        self.name = name
        self.project_name = project_name
        self.metadata = metadata

    def get_item(self, id: str) -> Vector:
        """Get a single vector by id"""
        resp = self.api.request(
            "GET",
            f"projects/{self.project_name}/collections/{self.name}/items/{id}",
        )

        return Vector.from_dict(resp)

    def insert(self, vector: Vector) -> None:
        """Insert a vector into the collection"""
        self.api.request(
            "POST",
            f"projects/{self.project_name}/collections/{self.name}/items",
            vector.to_dict(),
        )

    def insert_batch(self, vectors: list[Vector]) -> None:
        """Insert a list of vectors into the collection"""
        self.api.request(
            "POST",
            f"projects/{self.project_name}/collections/{self.name}/items/batch",
            {"vectors": [vector.to_dict() for vector in vectors]},
        )

    def search(self, query: list[float], limit: int = 5) -> list[CompVector]:
        """Search for the k closest vectors to the query vector"""
        resp = self.api.request(
            "POST",
            f"projects/{self.project_name}/collections/{self.name}/search",
            {"query": query, "limit": limit},
        )

        return [CompVector.from_dict(item) for item in resp]
