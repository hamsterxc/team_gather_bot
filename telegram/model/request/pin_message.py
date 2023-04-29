from .abstract_model import _AbstractModel


class PinMessageRequest(_AbstractModel):
    def __init__(self, chat_id: str, message_id: int):
        self.chat_id = chat_id
        self.message_id = message_id

    def __repr__(self) -> str:
        return f'PinMessageRequest(chat_id={self.chat_id}, message_id={self.message_id})'
