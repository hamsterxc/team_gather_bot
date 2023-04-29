from .abstract_model import _AbstractModel
from .chat import Chat
from .response import Response
from ..util import if_not_none


class Message(_AbstractModel):
    def __init__(self, json: dict):
        super().__init__(json)

        self.message_id = json.get('message_id')
        self.chat = if_not_none(json.get('chat'), lambda v: Chat(v))
        self.reply_to_message = if_not_none(json.get('reply_to_message'), lambda v: Message(v))
        self.text = json.get('text')

    def __repr__(self) -> str:
        return f'Message(message_id={self.message_id}, chat={self.chat}, reply_to_message={self.reply_to_message})'


class MessageResponse(Response):
    def __init__(self, json: dict):
        super().__init__(json)

        self.result = if_not_none(json.get('result'), lambda v: Message(v))
