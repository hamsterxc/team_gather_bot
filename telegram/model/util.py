def if_not_none(value, converter):
    return converter(value) if value is not None else None
