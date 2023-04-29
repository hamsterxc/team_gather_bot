class _DynamodbDocument:
    def to_dynamodb_json(self) -> dict:
        return None

    def _to_dynamodb_json(self, value) -> dict:
        if value is None:
            return {'NULL': True}
        elif isinstance(value, bool):
            return {'BOOL': value}
        elif isinstance(value, str):
            return {'S': value}
        elif isinstance(value, int):
            return {'N': str(value)}
        elif isinstance(value, list) or isinstance(value, set):
            return {'L': list(map(lambda v: self._to_dynamodb_json(v), value))}
        elif isinstance(value, dict):
            return {'M': {k: self._to_dynamodb_json(v) for k, v in value.items()}}
        else:
            return {'S': str(value)}

    def from_dynamodb_json(self, dynamodb_json: dict):
        return None

    def _from_dynamodb_json(self, dynamodb_json: dict):
        value = dynamodb_json.get('BOOL')
        if value is not None:
            return value.upper() == 'TRUE'

        value = dynamodb_json.get('S')
        if value is not None:
            return value

        value = dynamodb_json.get('N')
        if value is not None:
            return int(value)

        value = dynamodb_json.get('L')
        if value is not None:
            return map(lambda v: self._from_dynamodb_json(v), value)

        value = dynamodb_json.get('M')
        if value is not None:
            return {k: self._from_dynamodb_json(v) for k, v in value.items()}

        return None
