import requests

import logger
from .telegram_exception import TelegramException
from ..model.request.edit_message import EditMessageRequest
from ..model.request.get_updates import GetUpdatesRequest
from ..model.request.pin_message import PinMessageRequest
from ..model.request.send_message import SendMessageRequest
from ..model.request.unpin_message import UnpinMessageRequest
from ..model.response.message import MessageResponse, Message
from ..model.response.response import Response
from ..model.response.update import UpdateResponse, Update
from ..model.response.user import UserResponse, User
from ..model.util import to_json_string


class Telegram:

    _api_url = 'https://api.telegram.org'

    def __init__(self, token):
        self._url_base = self._api_url + '/bot' + token

    def get_me(self) -> User:
        return self._request(
            # lambda: requests.get(self._url_base + '/getMe'),
            lambda: self._send_request('GET', self._url_base + '/getMe'),
            lambda v: UserResponse(v),
            lambda v: v.result
        )

    def get_updates(self, request: GetUpdatesRequest = None) -> list[Update]:
        return self._request(
            # lambda: requests.post(self._url_base + '/getUpdates', json=request.to_json()),
            lambda: self._send_request('POST', self._url_base + '/getUpdates', body=request.to_json()),
            lambda v: UpdateResponse(v),
            lambda v: v.result
        )

    def send_message(self, request: SendMessageRequest) -> Message:
        return self._request(
            # lambda: requests.post(self._url_base + '/sendMessage', json=request.to_json()),
            lambda: self._send_request('POST', self._url_base + '/sendMessage', body=request.to_json()),
            lambda v: MessageResponse(v),
            lambda v: v.result
        )

    def edit_message(self, request: EditMessageRequest) -> Message:
        return self._request(
            lambda: self._send_request('POST', self._url_base + '/editMessageText', body=request.to_json()),
            lambda v: MessageResponse(v),
            lambda v: v.result
        )

    def pin_message(self, request: PinMessageRequest) -> Response:
        return self._request(
            lambda: self._send_request('POST', self._url_base + '/pinChatMessage', body=request.to_json()),
            lambda v: Response(v),
            lambda v: v
        )

    def unpin_message(self, request: UnpinMessageRequest) -> Response:
        return self._request(
            lambda: self._send_request('POST', self._url_base + '/unpinChatMessage', body=request.to_json()),
            lambda v: Response(v),
            lambda v: v
        )

    def _send_request(self, method: str, url: str, body: dict = None) -> requests.Response:
        logger.debug("--> {} {}".format(method, url))
        if body:
            logger.debug(to_json_string(body))

        response = requests.request(
            method,
            url,
            headers={'Content-Type': 'application/json'},
            data=to_json_string(body) if body is not None else None
        )

        logger.debug("<-- HTTP {}".format(response.status_code))
        text = response.text
        if text:
            logger.debug(str(text))

        return response

    def _request(self, requestor, response_builder, result_builder):
        api_response = requestor()
        json = api_response.json()
        response = response_builder(json)
        if response.ok:
            return result_builder(response)
        else:
            raise TelegramException(api_response.status_code, json)
