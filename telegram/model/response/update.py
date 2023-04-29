from .abstract_model import _AbstractModel
from .callback_query import CallbackQuery
from .message import Message
from .response import Response
from ..util import if_not_none


class Update(_AbstractModel):
    def __init__(self, json: dict):
        super().__init__(json)

        self.update_id = json.get('update_id')
        self.message = if_not_none(json.get('message'), lambda v: Message(v))
        self.callback_query = if_not_none(json.get('callback_query'), lambda v: CallbackQuery(v))


class UpdateResponse(Response):
    def __init__(self, json: dict):
        super().__init__(json)

        self.result = if_not_none(json.get('result'), lambda v: list(map(lambda v: Update(v), v)))
