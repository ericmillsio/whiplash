import os
from typing import Optional
from venv import logger

import numpy as np

from whiplash.collection import Collection
from whiplash.responses import error_response, parse_body, response
from whiplash.vector import Vector
from whiplash.whiplash import Whiplash

REGION = os.environ.get("REGION")
STAGE = os.environ.get("STAGE")


def _get_collection(event) -> Optional[Collection]:
    project_id = event["pathParameters"]["projectId"]
    collection_id = event["pathParameters"]["collectionId"]
    whiplash = Whiplash(REGION, STAGE, project_name=project_id)
    return whiplash.get_collection(collection_id)


def get(event, context):
    # Get item
    collection = _get_collection(event)
    if not collection:
        return error_response("Collection not found", 404)

    try:
        item = collection.get_item(event["pathParameters"]["itemId"])
    except Exception as e:
        logger.info(f"Error getting item: {e}")
        item = None

    if not item:
        return error_response("Item not found", 404)

    return response(item.to_dict())


def search(event, context):
    # Search collection
    collection = _get_collection(event)

    if not collection:
        return error_response("Collection not found", 404)

    body, error = parse_body(event)
    if not body or error:
        return error

    query = body.get("query", None)
    limit = body.get("limit", 5)

    if (
        not query
        or not isinstance(query, list)
        or len(query) != collection.config.n_features
    ):
        return error_response(
            "'query' is required and must be a n_features length list of floats"
        )

    query = np.array(query, dtype=np.float32)
    limit = int(limit)

    results = collection.search(query, k=limit)
    return response([result.to_dict() for result in results])


def create(event, context):
    # Create item from POST body
    collection = _get_collection(event)

    if not collection:
        return error_response("Collection not found", 404)

    body, error = parse_body(event)
    if not body or error:
        return error
    vector_id = body.get("id", None)
    if not vector_id:
        return error_response("'id' required")
    vector = body.get("vector", None)
    if not vector or len(vector) != collection.config.n_features:
        return error_response("'vector' required and must match 'n_features' in size")
    vector = Vector(vector_id, vector)
    collection.insert(vector)
    return response({"message": "success"})


def create_batch(event, context):
    # Create items from POST body
    collection = _get_collection(event)

    if not collection:
        return error_response("Collection not found", 404)

    body, error = parse_body(event)
    if not body or error:
        return error

    vectors = body.get("vectors", None)
    if not vectors:
        return error_response("'vectors' required")

    for vector in vectors:
        vector_id = vector.get("id", None)
        if not vector_id:
            return error_response("'id' required")
        vec = vector.get("vector", None)
        if not vec or len(vec) != collection.config.n_features:
            return error_response(
                "'vector' required and must match 'n_features' in size"
            )

        collection.insert(Vector(vector_id, np.array(vec, dtype=np.float32)))

    return response({"message": "success"})
