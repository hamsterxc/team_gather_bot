from .abstract_model import _AbstractModel
from .message import Message
from .user import User
from ..util import if_not_none


class CallbackQuery(_AbstractModel):
    def __init__(self, json: dict):
        super().__init__(json)

        self.id = json.get('id')
        self.from_user = if_not_none(json.get('from'), lambda v: User(v))
        self.message = if_not_none(json.get('message'), lambda v: Message(v))
        self.data = json.get('data')

    def __repr__(self) -> str:
        return f'CallbackQuery(id={self.id}, data={self.data})'
