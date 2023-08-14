import os

from whiplash.responses import error_response, response
from whiplash.whiplash import Whiplash

REGION = os.environ.get("REGION")
STAGE = os.environ.get("STAGE")


def get(event, context):
    # Get project metadata
    whiplash = Whiplash(
        REGION, STAGE, project_name=event["pathParameters"]["projectId"]
    )
    collections = [
        collection.to_dict()
        for collection in whiplash.get_all_collections()
        if collection.config.project_name == event["pathParameters"]["projectId"]
    ]

    if not collections or len(collections) == 0:
        return error_response("Project not found", 404)

    return response(
        {
            "project_name": event["pathParameters"]["projectId"],
            "collections": collections,
        }
    )


def all(event, context):
    # List projects
    whiplash = Whiplash(REGION, STAGE)
    collections = whiplash.get_all_collections()
    projects = {}
    for collection in collections:
        project_name = collection.config.project_name
        if project_name not in projects:
            projects[project_name] = {
                "project_name": project_name,
                "collections": [],
            }
        projects[project_name]["collections"].append(collection.to_dict())
    return response({"projects": projects})
