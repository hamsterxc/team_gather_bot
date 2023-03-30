from .aws_exception import AwsException
import logger


class Settings:
    _DEFAULT_TIMEZONE = 'Europe/Berlin'

    _table_name = 'team_gather_bot.settings'

    _dynamodb_client = None

    _entry_id: str = '1'
    timezone: str = 'Europe/Berlin'
    locale: str = 'en'
    last_update_id: int = -1
    last_update_time: int = 0
    last_gathering_id: str = '0'

    def __init__(self, dynamodb_client):
        self._dynamodb_client = dynamodb_client

        result = self._dynamodb_client.scan(TableName=self._table_name)
        logger.debug("Settings read: {}".format(str(result)))

        items = result['Items']
        items_len = len(items)
        if items_len == 0:
            pass
        elif items_len == 1:
            item = items[0]
            self._entry_id = item['id']['S']
            self.timezone = item['timezone']['S']
            self.locale = item['locale']['S']
            self.last_update_id = int(item['last_update_id']['N'])
            self.last_update_time = int(item['last_update_time']['N'])
            self.last_gathering_id = item['last_gathering_id']['S']
        else:
            raise AwsException("Non-unique settings entry: found {} entries".format(items_len))

    def next_gathering_id(self):
        id = int(self.last_gathering_id) + 1
        self.last_gathering_id = str(id)
        return id

    def save(self):
        item = {
            'id': {'S': self._entry_id},
            'timezone': {'S': self.timezone},
            'locale': {'S': self.locale},
            'last_update_id': {'N': str(self.last_update_id)},
            'last_update_time': {'N': str(self.last_update_time)},
            'last_gathering_id': {'S': self.last_gathering_id}
        }
        result = self._dynamodb_client.put_item(TableName=self._table_name, Item=item, ReturnValues='ALL_OLD')
        logger.debug("Settings saved: {}".format(str(result)))
