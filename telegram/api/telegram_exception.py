class TelegramException(BaseException):
    code: int
    description: str
    body: dict

    def __init__(self, status_code: int, json: dict):
        self.code = status_code
        self.description = json.get('description')
        self.body = json
        super().__init__("HTTP {}: {}".format(self.code, self.description))
