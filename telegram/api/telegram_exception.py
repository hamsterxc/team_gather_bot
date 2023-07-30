from telegram.model.util import to_json_string


class TelegramException(Exception):
    def __init__(self, status_code: int, json: dict):
        self.code = status_code
        self.description = json.get('description')
        self.body = to_json_string(json)

        super().__init__(f"HTTP {self.code}: {self.description}")

    def __repr__(self):
        return f"TelegramException, HTTP {self.code}: {self.body}"
