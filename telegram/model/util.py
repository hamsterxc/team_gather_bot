import json


def if_not_none(value, converter):
    return converter(value) if value is not None else None


def to_json_string(value: dict) -> str:
    return json.dumps({k: v for k, v in value.items() if v is not None})
