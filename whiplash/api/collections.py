import os

from whiplash.responses import parse_body, response
from whiplash.whiplash import Whiplash

REGION = os.environ.get("REGION")
STAGE = os.environ.get("STAGE")

DEFAULT_N_PLANES = int(os.environ.get("DEFAULT_N_PLANES", 6))
DEFAULT_BIT_START = int(os.environ.get("DEFAULT_BIT_START", 8))
DEFAULT_BIT_SCALE_FACTOR = float(os.environ.get("DEFAULT_BIT_SCALE_FACTOR", 2))


def get(event, context):
    # Get collection
    project_id = event["pathParameters"]["projectId"]
    collection_id = event["pathParameters"]["collectionId"]
    whiplash = Whiplash(REGION, STAGE, project_name=project_id)
    collection = whiplash.get_collection(collection_id)
    if not collection:
        return response({"message": "Collection not found"}, 404)
    return response(collection.to_dict())


def all(event, context):
    # List collections
    project_id = event["pathParameters"]["projectId"]
    whiplash = Whiplash(REGION, STAGE, project_name=project_id)
    collections = whiplash.get_all_collections()
    return response([collection.to_dict() for collection in collections])


def create(event, context):
    # Create project from POST body
    project_id = event["pathParameters"]["projectId"]
    body, error = parse_body(event)
    if not body or error:
        return error

    collection_name = body.get("collection_name", None)
    n_features = body.get("n_features", None)
    if not collection_name:
        return response({"message": "collection_name required"}, 400)
    if not n_features:
        return response({"message": "n_features required"}, 400)

    n_planes = body.get("n_planes", DEFAULT_N_PLANES)
    bit_start = body.get("bit_start", DEFAULT_BIT_START)
    bit_scale_factor = body.get("bit_scale_factor", DEFAULT_BIT_SCALE_FACTOR)

    whiplash = Whiplash(REGION, STAGE, project_name=project_id)
    collection = whiplash.create_collection(
        collection_name,
        n_features=n_features,
        n_planes=int(n_planes),
        bit_start=int(bit_start),
        bit_scale_factor=float(bit_scale_factor),
    )
    return response(collection.to_dict())
