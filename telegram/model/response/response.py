from .abstract_model import _AbstractModel


class Response(_AbstractModel):
    def __init__(self, json: dict):
        super().__init__(json)

        self.ok = json.get('ok')
        self.description = json.get('description')

    def __repr__(self) -> str:
        return f'Response(ok={self.ok}, description={self.description})'
