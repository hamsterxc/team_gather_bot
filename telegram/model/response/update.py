from .abstract_model import _AbstractModel
from .callback_query import CallbackQuery
from .message import Message
from .response import Response
from ..util import if_not_none


class Update(_AbstractModel):
    update_id: int
    message: Message
    callback_query: CallbackQuery

    def __init__(self, json):
        super().__init__(json)
        self.message = if_not_none(super()._field('message'), lambda v: Message(v))
        self.callback_query = if_not_none(super()._field('callback_query'), lambda v: CallbackQuery(v))


class UpdateResponse(Response):
    result: list

    def __init__(self, json):
        super().__init__(json)
        self.result = if_not_none(super()._field('result'), lambda v: list(map(lambda v: Update(v), v)))
