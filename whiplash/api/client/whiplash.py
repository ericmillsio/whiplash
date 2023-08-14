import logging
from typing import Optional

from whiplash.api.client.api_config import APIConfig
from whiplash.api.client.collection import Collection

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Whiplash:
    """Whiplash API Client"""

    api: APIConfig
    project_name: str

    def __init__(
        self,
        api_url: str,
        api_key: str,
        project_name: str = "whiplash",
    ) -> None:
        if not isinstance(api_url, str) or len(api_url) == 0:
            raise ValueError("api_url must be specified as a string")
        if not isinstance(api_key, str) or len(api_key) == 0:
            raise ValueError("api_key must be specified as a string")
        if not isinstance(project_name, str) or len(project_name) == 0:
            project_name = "whiplash"

        self.api = APIConfig(api_url, api_key)
        self.project_name = project_name

    def get_collections(self) -> list[Collection]:
        return [
            Collection(self.api, collection["name"], self.project_name, collection)
            for collection in self.api.request(
                "GET", f"projects/{self.project_name}/collections"
            )
        ]

    def create_collection(
        self,
        collection_name: str,
        n_features: int,
        n_planes: int = 6,
        bit_start: int = 8,
        bit_scale_factor: (float | int) = 2,
    ) -> Collection:
        metadata = self.api.request(
            "POST",
            f"projects/{self.project_name}/collections",
            {
                "name": collection_name,
                "n_features": n_features,
                "n_planes": n_planes,
                "bit_start": bit_start,
                "bit_scale_factor": bit_scale_factor,
            },
        )
        return Collection(self.api, collection_name, self.project_name, metadata)

    def get_collection(self, collection_name: str) -> Optional[Collection]:
        metadata = self.api.request(
            "GET",
            f"projects/{self.project_name}/collections/{collection_name}",
        )
        if metadata:
            return Collection(self.api, collection_name, self.project_name, metadata)
        return None
