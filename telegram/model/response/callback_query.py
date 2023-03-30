from .abstract_model import _AbstractModel
from .message import Message
from .user import User
from ..util import if_not_none


class CallbackQuery(_AbstractModel):
    id: str
    from_user: User
    message: Message
    data: str

    def __init__(self, json):
        super().__init__(json)
        self.from_user = if_not_none(super()._field('from'), lambda v: User(v))
        self.message = if_not_none(super()._field('message'), lambda v: Message(v))
