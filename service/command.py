from aws.gatherings import Gathering
from .telegram_command import AbstractTelegramCommand


class Command:
    def __init__(self):
        self._telegram_commands: list[AbstractTelegramCommand] = []
        self.gathering: Gathering = None

    def add_telegram_command(self, command: AbstractTelegramCommand):
        self._telegram_commands.append(command)

    def execute_telegram_commands(self):
        message_id = None
        for command in self._telegram_commands:
            if command.type == command.PIN and command.message_id is None:
                command.message_id = message_id

            result = command.execute()

            if command.type == command.SEND:
                message_id = result.message_id
                if self.gathering is not None:
                    self.gathering.message_id = message_id

    def __repr__(self) -> str:
        return f'Command(telegram_commands={self._telegram_commands}, gathering={self.gathering})'
