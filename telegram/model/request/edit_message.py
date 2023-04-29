from .abstract_model import _AbstractModel
from .send_message import InlineKeyboardMarkup
from ..util import if_not_none


class EditMessageRequest(_AbstractModel):
    def __init__(self, chat_id: str, message_id: int, text: str, parse_mode: str = None, reply_markup: InlineKeyboardMarkup = None):
        self.chat_id = chat_id
        self.message_id = message_id
        self.text = text
        self.parse_mode = parse_mode
        self.reply_markup = reply_markup

    def to_json(self) -> dict:
        json = super().to_json()
        json['reply_markup'] = if_not_none(self.reply_markup, lambda v: v.to_json())
        return json

    def __repr__(self) -> str:
        reply_markup = '<reply markup>' if self.reply_markup is not None else 'None'
        return f'EditMessageRequest(chat_id={self.chat_id}, message_id={self.message_id}, parse_mode={self.parse_mode}, reply_markup={reply_markup})'
