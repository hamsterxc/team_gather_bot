from .abstract_model import _AbstractModel
from ..util import if_not_none


MODE_MARKDOWN = 'MarkdownV2'
MODE_HTML = 'HTML'


class SendMessageRequest(_AbstractModel):
    def __init__(self, chat_id: str, text: str, parse_mode: str = None, reply_markup = None, reply_to_message_id: int = None):
        self.chat_id = chat_id
        self.text = text
        self.parse_mode = parse_mode
        self.reply_markup = reply_markup
        self.reply_to_message_id = reply_to_message_id

    def to_json(self) -> dict:
        json = super().to_json()
        json['reply_markup'] = if_not_none(self.reply_markup, lambda v: v.to_json())
        return json

    def __repr__(self) -> str:
        reply_markup = '<reply markup>' if self.reply_markup is not None else 'None'
        return f'SendMessageRequest(chat_id={self.chat_id}, parse_mode={self.parse_mode}, reply_markup={reply_markup}, reply_to_message_id={self.reply_to_message_id})'


class InlineKeyboardButton(_AbstractModel):
    def __init__(self, text: str, callback_data: str):
        self.text = text
        self.callback_data = callback_data


class InlineKeyboardMarkup(_AbstractModel):
    def __init__(self, inline_keyboard: list[list[InlineKeyboardButton]]):
        self.inline_keyboard = inline_keyboard

    def to_json(self):
        json = super().to_json()
        json['inline_keyboard'] = list(map(lambda row: list(map(lambda button: button.to_json(), row)), self.inline_keyboard))
        return json
