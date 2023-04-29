class _AbstractModel:
    def __init__(self, json: dict):
        self.__dict__.update(json)
