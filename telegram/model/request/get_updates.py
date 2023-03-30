from .abstract_model import _AbstractModel
from ..util import if_not_none


TYPE_MESSAGE = 'message'
TYPE_CALLBACK_QUERY = 'callback_query'


class GetUpdatesRequest(_AbstractModel):
    offset: int
    allowed_updates: list

    def __init__(self, offset: int = None, allowed_updates: list = None):
        self.offset = offset
        self.allowed_updates = if_not_none(allowed_updates, lambda v: list(map(lambda v: str(v), v)))
