import logger
from .aws_exception import AwsException
from .dynamodb_document import _DynamodbDocument


class Settings(_DynamodbDocument):
    _table_name = 'team_gather_bot.settings'

    def __init__(self, dynamodb_client):
        self._dynamodb_client = dynamodb_client

        result = self._dynamodb_client.scan(TableName=self._table_name)
        logger.debug(f"Settings read, dynamodb result: {result}")

        items = result['Items']
        items_len = len(items)
        if items_len == 0:
            self._entry_id = '1'
            self.timezone = 'Europe/Berlin'
            self.locale = 'en'
            self.last_update_id = -1
            self.last_update_time = 0
            self.last_gathering_id = '0'
        elif items_len == 1:
            item = items[0]
            self._entry_id = self._from_dynamodb_json(item['id'])
            self.timezone = self._from_dynamodb_json(item['timezone'])
            self.locale = self._from_dynamodb_json(item['locale'])
            self.last_update_id = self._from_dynamodb_json(item['last_update_id'])
            self.last_update_time = self._from_dynamodb_json(item['last_update_time'])
            self.last_gathering_id = self._from_dynamodb_json(item['last_gathering_id'])
        else:
            raise AwsException("Non-unique settings entry: found {} entries".format(items_len))

        logger.debug(f"Settings read: {self}")

    def next_gathering_id(self) -> str:
        self.last_gathering_id = str(int(self.last_gathering_id) + 1)
        return self.last_gathering_id

    def save(self):
        item = {
            'id': self._to_dynamodb_json(self._entry_id),
            'timezone': self._to_dynamodb_json(self.timezone),
            'locale': self._to_dynamodb_json(self.locale),
            'last_update_id': self._to_dynamodb_json(self.last_update_id),
            'last_update_time': self._to_dynamodb_json(self.last_update_time),
            'last_gathering_id': self._to_dynamodb_json(self.last_gathering_id),
        }
        result = self._dynamodb_client.put_item(TableName=self._table_name, Item=item, ReturnValues='ALL_OLD')
        logger.debug(f"Settings saved, dynamodb result: {result}")
        logger.debug(f"Settings saved: {self}")

    def __repr__(self) -> str:
        return str(self.__dict__)
