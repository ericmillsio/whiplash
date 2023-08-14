from decimal import Decimal

from boto3.dynamodb.types import Binary


def _clean_item(obj):
    if isinstance(obj, list):
        for i in range(len(obj)):
            obj[i] = _clean_item(obj[i])
        return obj
    elif isinstance(obj, dict):
        for k in obj.keys():
            obj[k] = _clean_item(obj[k])
        return obj
    elif isinstance(obj, Decimal):
        if obj % 1 == 0:
            return int(obj)
        else:
            return float(obj)
    elif isinstance(obj, Binary):
        return obj.value
    else:
        return obj


def clean_item(obj: dict) -> dict:
    for k in obj.keys():
        obj[k] = _clean_item(obj[k])
    return obj
