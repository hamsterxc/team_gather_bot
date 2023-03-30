from .abstract_model import _AbstractModel
from .response import Response
from .chat import Chat
from ..util import if_not_none


class Message(_AbstractModel):
    message_id: int
    chat: Chat
    text: str

    def __init__(self, json):
        super().__init__(json)
        self.chat = Chat(self.chat)


class MessageResponse(Response):
    result: Message

    def __init__(self, json):
        super().__init__(json)
        self.result = if_not_none(super()._field('result'), lambda v: Message(v))
