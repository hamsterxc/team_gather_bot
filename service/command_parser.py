from .parse_exception import ParseException


_STATE_ACTION = 0
_STATE_EXPECT_WHITESPACE = 1
_STATE_WHITESPACE = 2
_STATE_KEY = 3
_STATE_EXPECT_VALUE = 4
_STATE_VALUE = 5
_STATE_QUOTED_VALUE = 6
_STATE_ESCAPE = 7

_state_name = {
    _STATE_ACTION: 'ACTION',
    _STATE_EXPECT_WHITESPACE: 'EXPECT_WHITESPACE',
    _STATE_WHITESPACE: 'WHITESPACE',
    _STATE_KEY: 'KEY',
    _STATE_EXPECT_VALUE: 'EXPECT_VALUE',
    _STATE_VALUE: 'VALUE',
    _STATE_QUOTED_VALUE: 'QUOTED_VALUE',
    _STATE_ESCAPE: 'ESCAPE',
}


class Command:
    def __init__(self, action: str, arguments: dict):
        self.action = action
        self.arguments = arguments


def parse(command: str, parse_action: bool) -> Command:
    action = None
    arguments = {}

    state = _STATE_ACTION if parse_action else _STATE_WHITESPACE
    key = ''
    value = ''
    for c in command:
        if state == _STATE_ACTION:
            if _is_valid_unquoted(c):
                value += c
            elif c.isspace():
                action = value
                value = ''
                state = _STATE_WHITESPACE
            else:
                raise ParseException(command, "command", f"expected alphanumeric, underscore or whitespace in state {_get_state_name(state)}, got '{c}'")
        elif state == _STATE_WHITESPACE:
            if _is_valid_unquoted(c):
                state = _STATE_KEY
                key += c
            elif c.isspace():
                pass
            else:
                raise ParseException(command, "command", f"expected alphanumeric, underscore or whitespace in state {_get_state_name(state)}, got '{c}'")
        elif state == _STATE_EXPECT_WHITESPACE:
            if c.isspace():
                state = _STATE_WHITESPACE
            else:
                raise ParseException(command, "command", f"expected whitespace in state {_get_state_name(state)}, got '{c}'")
        elif state == _STATE_KEY:
            if _is_valid_unquoted(c):
                key += c
            elif c == ':':
                if len(key) == 0:
                    raise ParseException(command, "command", "expected key name")
                state = _STATE_EXPECT_VALUE
            else:
                raise ParseException(command, "command", f"expected alphanumeric, underscore or colon in state {_get_state_name(state)}, got '{c}'")
        elif state == _STATE_EXPECT_VALUE:
            if c == '"':
                state = _STATE_QUOTED_VALUE
            elif _is_valid_unquoted(c):
                value += c
                state = _STATE_VALUE
            elif c.isspace():
                arguments[key] = value
                key = ''
                value = ''
            else:
                raise ParseException(command, "command", f"expected alphanumeric, underscore, whitespace or quote in state {_get_state_name(state)}, got '{c}'")
        elif state == _STATE_VALUE:
            if _is_valid_unquoted(c):
                value += c
            elif c.isspace():
                arguments[key] = value
                key = ''
                value = ''
                state = _STATE_WHITESPACE
            else:
                raise ParseException(command, "command", f"expected alphanumeric, underscore or whitespace in state {_get_state_name(state)}, got '{c}'")
        elif state == _STATE_QUOTED_VALUE:
            if c == '"':
                arguments[key] = value
                key = ''
                value = ''
                state = _STATE_EXPECT_WHITESPACE
            elif c == '\\':
                state = _STATE_ESCAPE
            else:
                value += c
        elif state == _STATE_ESCAPE:
            value += c
            state = _STATE_QUOTED_VALUE
        else:
            raise ParseException(command, "command", f"unexpected state {_get_state_name(state)}")
    if state == _STATE_ACTION:
        action = value if len(value) > 0 else None
    elif state == _STATE_WHITESPACE or state == _STATE_EXPECT_WHITESPACE or state == _STATE_VALUE:
        if len(key) > 0:
            arguments[key] = value
    else:
        raise ParseException(command, "command", f"invalid end state {_get_state_name(state)}")

    return Command(action, arguments)


def _is_valid_unquoted(c: str) -> bool:
    return c.isalnum() or c == '_'


def _get_state_name(state: int) -> str:
    return _state_name.get(state, str(state))
