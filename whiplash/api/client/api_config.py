import logging
import traceback
from dataclasses import dataclass
from typing import Optional

import requests

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@dataclass
class APIConfig:
    url: str
    key: str

    def request(self, method: str, path: str, data: Optional[dict] = None) -> dict:
        try:
            response = requests.request(
                method,
                f"{self.url}/{path}",
                headers={"x-api-key": self.key, "Content-Type": "application/json"},
                json=data,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error making request: {e}")
            traceback.print_exc()
            return {}
