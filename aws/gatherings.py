import logger


class Gathering:
    id: str
    chat_id: str
    message_id: int
    is_started: bool
    start: int
    end: int
    max_count: int
    participants_yes: set
    participants_maybe: set
    participants_no: set
    message_text: str
    message_what: str
    message_where: str
    message_when: str

    def to_dynamodb_json(self) -> dict:
        return {
            'id': {'S': self.id},
            'chat_id': {'S': self.chat_id},
            'message_id': {'N': str(self.message_id)},
            'is_started': {'BOOL': self.is_started},
            'start': {'N': str(self.start)},
            'end': {'N': str(self.end)},
            'max_count': {'N': str(self.max_count)},
            'participants': {'M': {
                'yes': {'L': list(map(lambda v: {'S': v}, self.participants_yes))},
                'maybe': {'L': list(map(lambda v: {'S': v}, self.participants_maybe))},
                'no': {'L': list(map(lambda v: {'S': v}, self.participants_no))},
            }},
            'message': {'M': {
                'text': {'S': self.message_text},
                'what': {'S': self.message_what},
                'where': {'S': self.message_where},
                'when': {'S': self.message_when},
            }},
        }

    @staticmethod
    def from_dynamodb_json(dynamodb_json: dict):
        gathering = Gathering()

        gathering.id = dynamodb_json['id']['S']
        gathering.chat_id = dynamodb_json['chat_id']['S']
        gathering.message_id = int(dynamodb_json['message_id']['N'])
        gathering.is_started = dynamodb_json['is_started']['BOOL']
        gathering.start = int(dynamodb_json['start']['N'])
        gathering.end = int(dynamodb_json['end']['N'])
        gathering.max_count = int(dynamodb_json['max_count']['N'])
        gathering.participants_yes = set(map(lambda v: v['S'], dynamodb_json['participants']['M']['yes']['L']))
        gathering.participants_maybe = set(map(lambda v: v['S'], dynamodb_json['participants']['M']['maybe']['L']))
        gathering.participants_no = set(map(lambda v: v['S'], dynamodb_json['participants']['M']['no']['L']))
        gathering.message_text = dynamodb_json['message']['M']['text']['S']
        gathering.message_what = dynamodb_json['message']['M']['what']['S']
        gathering.message_where = dynamodb_json['message']['M']['where']['S']
        gathering.message_when = dynamodb_json['message']['M']['when']['S']

        return gathering

    @staticmethod
    def create_new(
            id: str,
            chat_id: str,
            start: int,
            end: int,
            max_count: int,
            message_text: str,
            message_what: str,
            message_where: str,
            message_when: str
    ):
        gathering = Gathering()

        gathering.id = id
        gathering.chat_id = chat_id
        gathering.message_id = None
        gathering.is_started = False
        gathering.start = start
        gathering.end = end
        gathering.max_count = max_count
        gathering.participants_yes = []
        gathering.participants_maybe = []
        gathering.participants_no = []
        gathering.message_text = message_text
        gathering.message_what = message_what
        gathering.message_where = message_where
        gathering.message_when = message_when

        return gathering


def _is_equal(first: Gathering, second: Gathering) -> bool:
    return (first.chat_id == second.chat_id) \
        and (first.message_id == second.message_id) \
        and (first.is_started == second.is_started) \
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


class Gatherings:
    _table_name = 'team_gather_bot.gatherings'

    _dynamodb_client = None

    gatherings: dict
    _gatherings_original: dict

    def __init__(self, dynamodb_client):
        self._dynamodb_client = dynamodb_client

        result = self._dynamodb_client.scan(TableName=self._table_name)
        logger.debug("Gatherings read: {}".format(str(result)))

        self.gatherings = self._from_dynamodb_json(result)
        self._gatherings_original = self._from_dynamodb_json(result)

    def _from_dynamodb_json(self, dynamodb_json_items):
        return {v.id: v for v in map(lambda dynamodb_json: Gathering.from_dynamodb_json(dynamodb_json), dynamodb_json_items['Items'])}

    def get_all(self):
        return self.gatherings

    def add(self, gathering: Gathering):
        self.gatherings[gathering.id] = gathering

    def remove(self, id: str):
        del self.gatherings[id]

    def save(self):
        request_items = []

        for id, gathering in self.gatherings:
            original = self._gatherings_original.get(id)
            if not _is_equal(gathering, original):
                request_items.append({'PutRequest': {'Item': {id: gathering.to_dynamodb_json()}}})

        for id, original in self._gatherings_original:
            if id not in self.gatherings:
                request_items.append({'DeleteRequest': {'Key': {'id': {'S': id}}}})

        self._dynamodb_client.batch_write_item(RequestItems={self._table_name: request_items})

        dynamodb_json_items = {'Items': list(map(lambda v: v.to_dynamodb_json(), self.gatherings))}
        self.gatherings = self._from_dynamodb_json(dynamodb_json_items)
        self._gatherings_original = self._from_dynamodb_json(dynamodb_json_items)
