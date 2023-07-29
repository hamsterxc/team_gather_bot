import logger
from aws.aws_exception import AwsException
from aws.dynamodb_document import _DynamodbDocument

STATE_SCHEDULED = 0
STATE_STARTED = 1
STATE_STOPPED = 2


class Gathering(_DynamodbDocument):
    def __init__(self):
        self.id = None
        self.chat_id = None
        self.message_id = None
        self.state = None
        self.start = None
        self.end = None
        self.max_count = None
        self.participants_yes: set[str] = set()
        self.participants_maybe: set[str] = set()
        self.participants_no: set[str] = set()
        self.message_text = None
        self.message_what = None
        self.message_where = None
        self.message_when = None

    def to_dynamodb_json(self) -> dict:
        return {
            'id': self._to_dynamodb_json(self.id),
            'chat_id': self._to_dynamodb_json(self.chat_id),
            'message_id': self._to_dynamodb_json(self.message_id),
            'state': self._to_dynamodb_json(self.state),
            'start': self._to_dynamodb_json(self.start),
            'end': self._to_dynamodb_json(self.end),
            'max_count': self._to_dynamodb_json(self.max_count),
            'participants': self._to_dynamodb_json({
                'yes': self.participants_yes,
                'maybe': self.participants_maybe,
                'no': self.participants_no,
            }),
            'message': self._to_dynamodb_json({
                'text': self.message_text,
                'what': self.message_what,
                'where': self.message_where,
                'when': self.message_when,
            }),
        }

    def from_dynamodb_json(self, dynamodb_json: dict):
        self.id = self._from_dynamodb_json(dynamodb_json['id'])
        self.chat_id = self._from_dynamodb_json(dynamodb_json['chat_id'])
        self.message_id = self._from_dynamodb_json(dynamodb_json['message_id'])
        self.state = self._from_dynamodb_json(dynamodb_json['state'])
        self.start = self._from_dynamodb_json(dynamodb_json['start'])
        self.end = self._from_dynamodb_json(dynamodb_json['end'])
        self.max_count = self._from_dynamodb_json(dynamodb_json['max_count'])

        participants = self._from_dynamodb_json(dynamodb_json['participants'])
        self.participants_yes = set(participants['yes'])
        self.participants_maybe = set(participants['maybe'])
        self.participants_no = set(participants['no'])

        messages = self._from_dynamodb_json(dynamodb_json['message'])
        self.message_text = messages.get('text')
        self.message_what = messages.get('what')
        self.message_where = messages.get('where')
        self.message_when = messages.get('when')

        return self

    def __repr__(self) -> str:
        return str(self.__dict__)


class Gatherings:
    _table_name = 'team_gather_bot.gatherings'

    def __init__(self, dynamodb_client):
        self._dynamodb_client = dynamodb_client

        result = self._dynamodb_client.scan(
            TableName=self._table_name,
            FilterExpression='#state <> :state',
            ExpressionAttributeNames={'#state': 'state'},
            ExpressionAttributeValues={':state': _DynamodbDocument._to_dynamodb_json(_DynamodbDocument(), STATE_STOPPED)}
        )
        logger.debug(f"Gatherings read, dynamodb result: {result}")

        self.gatherings: dict[str, Gathering] = self._from_dynamodb_json(result)
        self._gatherings_original: dict[str, Gathering] = self._from_dynamodb_json(result)

        logger.debug(f"Gatherings read: {self.gatherings}")

    def _from_dynamodb_json(self, dynamodb_json_items) -> dict[str, Gathering]:
        return {v.id: v for v in map(lambda dynamodb_json: Gathering.from_dynamodb_json(Gathering(), dynamodb_json), dynamodb_json_items['Items'])}

    def get_by_message_id(self, message_id: int) -> Gathering:
        gatherings = {v for k, v in self.gatherings.items() if v.message_id == message_id}
        gatherings_len = len(gatherings)
        if gatherings_len == 0:
            return None
        elif gatherings_len == 1:
            return gatherings.pop()
        else:
            raise AwsException(f"Non-unique gatherings by message_id {message_id} found: {gatherings_len} entries")

    def get_all(self):
        return self.gatherings

    def save(self, gathering: Gathering):
        original = self._gatherings_original.get(gathering.id)
        if original is None or not self._is_equal(gathering, original):
            json = gathering.to_dynamodb_json()
            result = self._dynamodb_client.put_item(TableName=self._table_name, Item=json)
            logger.debug(f"Gathering saved, dynamodb result: {result}")
            logger.debug(f"Gathering saved: {json}")
        self._gatherings_original[gathering.id] = gathering

    def _is_equal(self, first: Gathering, second: Gathering) -> bool:
        return (first.chat_id == second.chat_id) \
            and (first.message_id == second.message_id) \
            and (first.state == second.state) \
            and (first.start == second.start) \
            and (first.end == second.end) \
            and (first.max_count == second.max_count) \
            and (first.participants_yes == second.participants_yes) \
            and (first.participants_maybe == second.participants_maybe) \
            and (first.participants_no == second.participants_no) \
            and (first.message_text == second.message_text) \
            and (first.message_what == second.message_what) \
            and (first.message_where == second.message_where) \
            and (first.message_when == second.message_when)
