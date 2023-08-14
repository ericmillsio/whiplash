import logging
import time
from typing import Optional

from botocore.exceptions import ClientError

from whiplash.collection import Collection
from whiplash.collection_config import CollectionConfig
from whiplash.storage import DynamoStorage

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Whiplash:
    region: str
    stage: str
    config: (dict | None)
    project_name: str

    def __init__(
        self,
        region,
        stage,
        project_name: str = "whiplash",
    ) -> None:
        if not isinstance(region, str):
            raise ValueError("region must be specified as a string")
        if not isinstance(stage, str):
            raise ValueError("stage must be specified as a string")
        if not isinstance(project_name, str):
            raise ValueError("project_name must be specified as a string")

        self.region = region
        self.stage = stage
        self.project_name = project_name
        self.storage = DynamoStorage()
        self.metadata_table = self.storage.get_table("whiplash_metadata")

    def __repr__(self) -> str:
        return f"Whiplash(region={self.region}, stage={self.stage}, project_name={self.project_name})"

    def setup(self):
        self.metadata_table.create_table()
        while True:
            try:
                self.metadata_table.describe_table()
                break
            except Exception:
                time.sleep(1)

    def get_all_collections(self) -> list[Collection]:
        # Get all items from metadata table
        try:
            return [
                Collection.from_dict(collection)
                for collection in self.metadata_table.dump()
            ]
        except Exception as e:
            logger.error(f"Error getting all projects: {e}")
            return []

    def create_collection(
        self,
        collection_name: str,
        n_features: int,
        n_planes: int = 6,
        bit_start: int = 8,
        bit_scale_factor: (float | int) = 2,
    ) -> Collection:
        # Create collection in DynamoDB
        collection = self.get_collection(collection_name)
        if collection is not None:
            raise ValueError(f"Collection already exists: {collection_name}")

        collection_config = CollectionConfig(
            collection_name,
            self.region,
            self.stage,
            self.project_name,
            n_features,
            n_planes,
            bit_start,
            bit_scale_factor,
        )
        collection_config.create_uniform_planes()

        self.metadata_table.put(collection_config.to_dynamo())
        collection = Collection(collection_config)
        collection.create()
        return collection

    def get_collection(self, collection_name: str) -> Optional[Collection]:
        # Get collection info from DynamoDB
        collection_id = f"{self.project_name}_{self.stage}_{collection_name}"
        collection_config = self.metadata_table.get(collection_id)

        if collection_config is None:
            return None

        return Collection.from_dict(collection_config)
