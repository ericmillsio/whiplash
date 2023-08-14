import json
import logging
from dataclasses import dataclass
from http import HTTPStatus
from typing import Any, List, Optional, Tuple, Type, Union

logger = logging.getLogger(__name__)

cors_headers = {
    "Access-Control-Allow-Origin": "*",
    "Content-Type": "application/json",
}


@dataclass
class ErrorContent:
    status: int
    message: str


@dataclass
class ErrorResponse:
    error: ErrorContent


def basic_response(body: dict, status_code=HTTPStatus.OK.value):
    resp = {
        "headers": cors_headers,
        "statusCode": status_code,
        "body": json.dumps(body),
    }
    return resp


def empty_response(status_code=HTTPStatus.OK.value):
    resp = {"headers": cors_headers, "statusCode": status_code, "body": ""}
    return resp


def response(body: Union[object, List[object]], status_code=HTTPStatus.OK.value):
    resp = {
        "headers": cors_headers,
        "statusCode": status_code,
        "body": json.dumps(body),
    }
    return resp


def error_response(msg, status_code=HTTPStatus.BAD_REQUEST.value):
    err = ErrorContent(message=msg, status=status_code)
    resp = ErrorResponse(error=err)
    return response(resp, status_code)


def unauthorized_response():
    return error_response("Unauthorized.", HTTPStatus.UNAUTHORIZED.value)


def parse_body(event: dict) -> Tuple[Optional[dict], Any]:
    if "body" not in event or event["body"] is None:
        logger.error("Invalid body in event: %s", event)
        return None, error_response("No data provided", HTTPStatus.BAD_REQUEST.value)

    try:
        if isinstance(event["body"], str):
            body = json.loads(event["body"])
        else:
            body = event["body"]
    except TypeError as e:
        logger.exception(e)
        return None, error_response(
            f"Request failed to validate body: {str(e)}",
            HTTPStatus.BAD_REQUEST.value,
        )

    return body, None


def parse_request(event: dict, model: Type[object], field: str = "body"):
    if field not in event or event[field] is None:
        logger.error("Invalid body in event: %s", event)
        return None, error_response(
            f"Request does not match expected body: {model.__name__}",
            HTTPStatus.BAD_REQUEST.value,
        )

    logger.info(event[field])
    logger.info(event)
    try:
        if isinstance(event[field], str):
            field_value = json.loads(event[field])
        else:
            field_value = event[field]
        api_request = model(**field_value)
    except TypeError as e:
        logger.exception(e)
        return None, error_response(
            f"Request failed to validate {field}: {str(e)}",
            HTTPStatus.BAD_REQUEST.value,
        )

    return api_request, None


def get_api_key(event):
    session = event.get("requestContext", {}).get("identity", {}).get("apiKey", None)
    # Fallback value for local development and prod
    if not session or session == "offlineContext_apiKey":
        session = event.get("headers", {}).get(
            "x-api-key", event.get("headers", {}).get("X-Api-Key", None)
        )

    return session
