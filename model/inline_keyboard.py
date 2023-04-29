from telegram.model.request.send_message import InlineKeyboardMarkup, InlineKeyboardButton


class _InlineKeyboardButton:
    def __init__(self, text: str, data: str):
        self.text = text
        self.data = data


class InlineKeyboard:
    def __init__(self):
        self._buttons: list[list[_InlineKeyboardButton]] = []

    def add_row(self):
        self._buttons.append([])
        return self

    def add_button(self, text: str, data: str):
        self._buttons[-1].append(_InlineKeyboardButton(text, data))
        return self

    def to_telegram_model(self):
        return InlineKeyboardMarkup(list(map(
            lambda row: list(map(
                lambda button: InlineKeyboardButton(button.text, button.data),
                row)),
            self._buttons)))
