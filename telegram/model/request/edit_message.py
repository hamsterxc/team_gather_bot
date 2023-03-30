from .abstract_model import _AbstractModel
from ..util import if_not_none
from .send_message import InlineKeyboardMarkup


class EditMessageRequest(_AbstractModel):
    chat_id: str
    message_id: int
    text: str
    parse_mode: str
    reply_markup: InlineKeyboardMarkup

    def __init__(self, chat_id: str, message_id: int, text: str, parse_mode: str = None, reply_markup: InlineKeyboardMarkup = None):
        self.chat_id = chat_id
        self.message_id = message_id
        self.text = text
        self.parse_mode = parse_mode
        self.reply_markup = reply_markup

    def to_json(self):
        json = super().to_json()
        json['reply_markup'] = if_not_none(json['reply_markup'], lambda v: v.to_json())
        return json
