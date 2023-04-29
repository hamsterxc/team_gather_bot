from .abstract_model import _AbstractModel
from .response import Response
from ..util import if_not_none


class User(_AbstractModel):
    def __init__(self, json: dict):
        super().__init__(json)

        self.id = json.get('id')
        self.first_name = json.get('first_name')
        self.username = json.get('username')

    def name(self):
        return '@' + self.username if self.username is not None else self.first_name

    def __repr__(self) -> str:
        return f'User(id={self.id}, first_name={self.first_name}, username={self.username})'


class UserResponse(Response):
    def __init__(self, json: dict):
        super().__init__(json)

        self.result = if_not_none(json.get('result'), lambda v: User(v))
