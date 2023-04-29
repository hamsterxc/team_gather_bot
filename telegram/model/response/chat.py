from .abstract_model import _AbstractModel


class Chat(_AbstractModel):
    def __init__(self, json: dict):
        super().__init__(json)

        self.id = str(json.get('id'))

    def __repr__(self) -> str:
        return f'Chat(id={self.id})'
