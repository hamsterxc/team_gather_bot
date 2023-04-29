from .abstract_model import _AbstractModel

TYPE_MESSAGE = 'message'
TYPE_CALLBACK_QUERY = 'callback_query'


class GetUpdatesRequest(_AbstractModel):
    def __init__(self, offset: int = None, allowed_updates: list[str] = None):
        self.offset = offset
        self.allowed_updates = allowed_updates

    def __repr__(self) -> str:
        return f'GetUpdatesRequest(offset={self.offset}, allowed_updates={self.allowed_updates})'
