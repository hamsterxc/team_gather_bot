from .abstract_model import _AbstractModel


class UnpinMessageRequest(_AbstractModel):
    def __init__(self, chat_id: str, message_id: int = None):
        self.chat_id = chat_id
        self.message_id = message_id

    def __repr__(self) -> str:
        return f'UnpinMessageRequest(chat_id={self.chat_id}, message_id={self.message_id})'
