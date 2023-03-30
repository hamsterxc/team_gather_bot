class _AbstractModel:
    def __init__(self, json):
        self.__dict__.update(json)

    def _field(self, name):
        return self.__dict__.get(name)
