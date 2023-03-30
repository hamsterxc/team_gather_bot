from .abstract_model import _AbstractModel
from .response import Response


class User(_AbstractModel):
    id: int
    first_name: str
    username: str


class UserResponse(Response):
    result: User

    def __init__(self, json):
        super().__init__(json)
        self.result = User(self.result)
