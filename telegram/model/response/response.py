from .abstract_model import _AbstractModel


class Response(_AbstractModel):
    ok: bool
    description: str
