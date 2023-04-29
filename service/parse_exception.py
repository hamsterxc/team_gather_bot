class ParseException(Exception):
    def __init__(self, input: str, type: str = None, message: str = None):
        super().__init__("Invalid {} '{}'{}".format(
            type if type is not None else "input",
            input,
            ": " + message if message is not None else ""
        ))
