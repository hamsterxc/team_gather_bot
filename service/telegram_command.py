import logger
from telegram.api.telegram_api import Telegram
from telegram.api.telegram_exception import TelegramException
from telegram.model.request.edit_message import EditMessageRequest
from telegram.model.request.pin_message import PinMessageRequest
from telegram.model.request.send_message import SendMessageRequest, MODE_HTML
from telegram.model.request.unpin_message import UnpinMessageRequest


class AbstractTelegramCommand:
    SEND = 0
    SEND_SILENT = 1
    EDIT = 2
    PIN = 3
    UNPIN = 4

    def __init__(self, telegram: Telegram, i18n, type: int):
        self.telegram = telegram
        self.i18n = i18n
        self.type = type
        
    def _execute(self, chat_id: str, message_id: int, action):
        try:
            return action()
        except TelegramException as e:
            logger.error(f"Telegram error {e.code}: {e.body}")
            try:
                self.telegram.send_message(SendMessageRequest(
                    chat_id=chat_id,
                    text=self.i18n.TELEGRAM_ERROR.format(e.code, e.description),
                    parse_mode=MODE_HTML,
                    reply_to_message_id=message_id
                ))
            except TelegramException as e_nested:
                logger.error(f"Telegram error {e_nested.code}: {e_nested.body}")
        return None

    def execute(self):
        return None

    def __repr__(self) -> str:
        return f'AbstractTelegramCommand(type={self.type})'


class SendMessageCommand(AbstractTelegramCommand):
    def __init__(self, telegram: Telegram, i18n, send_message_request: SendMessageRequest, is_updating: bool = True):
        super().__init__(telegram, i18n, self.SEND if is_updating else self.SEND_SILENT)
        self.send_message_request = send_message_request
        
    def execute(self):
        return super()._execute(
            self.send_message_request.chat_id,
            self.send_message_request.reply_to_message_id,
            lambda: self.telegram.send_message(self.send_message_request)
        )

    def __repr__(self) -> str:
        return f'SendMessageCommand({self.send_message_request})'


class EditMessageCommand(AbstractTelegramCommand):
    def __init__(self, telegram: Telegram, i18n, edit_message_request: EditMessageRequest):
        super().__init__(telegram, i18n, self.EDIT)
        self.edit_message_request = edit_message_request

    def execute(self):
        return super()._execute(
            self.edit_message_request.chat_id,
            self.edit_message_request.message_id,
            lambda: self.telegram.edit_message(self.edit_message_request)
        )

    def __repr__(self) -> str:
        return f'EditMessageCommand({self.edit_message_request})'


class PinMessageCommand(AbstractTelegramCommand):
    def __init__(self, telegram: Telegram, i18n, chat_id: str, message_id: int = None):
        super().__init__(telegram, i18n, self.PIN)
        self.chat_id = chat_id
        self.message_id = message_id

    def execute(self):
        return super()._execute(
            self.chat_id,
            self.message_id,
            lambda: self.telegram.pin_message(PinMessageRequest(
                chat_id=self.chat_id,
                message_id=self.message_id
            ))
        )

    def __repr__(self) -> str:
        return f'PinMessageCommand(chat_id={self.chat_id}, message_id={self.message_id})'


class UnpinMessageCommand(AbstractTelegramCommand):
    def __init__(self, telegram: Telegram, i18n, chat_id: str, message_id: int):
        super().__init__(telegram, i18n, self.UNPIN)
        self.chat_id = chat_id
        self.message_id = message_id

    def execute(self):
        return super()._execute(
            self.chat_id,
            self.message_id,
            lambda: self.telegram.unpin_message(UnpinMessageRequest(
                chat_id=self.chat_id,
                message_id=self.message_id
            ))
        )

    def __repr__(self) -> str:
        return f'UnpinMessageCommand(chat_id={self.chat_id}, message_id={self.message_id})'
