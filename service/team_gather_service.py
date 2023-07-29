import logger
from aws.gatherings import Gatherings, Gathering, STATE_SCHEDULED, STATE_STARTED, STATE_STOPPED
from aws.settings import Settings
from model.inline_keyboard import InlineKeyboard
from telegram.api.telegram_api import Telegram
from telegram.model.request.edit_message import EditMessageRequest
from telegram.model.request.get_updates import GetUpdatesRequest, TYPE_MESSAGE, TYPE_CALLBACK_QUERY
from telegram.model.request.send_message import SendMessageRequest, MODE_HTML, InlineKeyboardMarkup
from telegram.model.response.callback_query import CallbackQuery
from telegram.model.response.message import Message
from .command import Command
from .command_parser import parse as parse_command
from .parse_exception import ParseException
from .telegram_command import SendMessageCommand, PinMessageCommand, UnpinMessageCommand, AbstractTelegramCommand, EditMessageCommand
from .time_parser import TimeParser


class TeamGatherService:
    def __init__(self, telegram: Telegram, settings: Settings, gatherings: Gatherings, i18n, time_parser: TimeParser):
        self._telegram = telegram
        self._settings = settings
        self._gatherings = gatherings
        self._i18n = i18n
        self._time_parser = time_parser

    def handle_events(self):
        # a deduplication mechanism not to send Telegram messages or save DynamoDB entries for the same gathering more than once
        commands: dict[str, Command] = dict()
        for id, gathering in self._gatherings.get_all().items():
            command = Command()
            command.gathering = gathering
            commands[id] = command

        # process Telegram updates
        me = self._telegram.get_me()
        updates = self._telegram.get_updates(GetUpdatesRequest(
            offset=self._settings.last_update_id + 1,
            allowed_updates=[TYPE_MESSAGE, TYPE_CALLBACK_QUERY]
        ))
        for update in updates:
            command = None
            if update.message is not None:
                message = update.message
                prefix = '@{} '.format(me.username)
                if message.text and message.text.startswith(prefix):
                    command_text = message.text.removeprefix(prefix).strip()
                    command = self._handle_command(message, command_text)
                    logger.info(f"Processed update: {command_text}; result: {command}")
            elif update.callback_query is not None:
                command = self._handle_callback(update.callback_query)
                logger.info(f"Processed callback: {update.callback_query}; result: {command}")
            self._settings.last_update_id = update.update_id

            if command is not None:
                if command.gathering is not None:
                    commands[command.gathering.id] = command
                else:
                    command.execute_telegram_commands()

        # process time-based events (on a "tick")
        for id, command in commands.items():
            tick_command = self._handle_tick(command.gathering)
            if tick_command is not None:
                commands[id] = tick_command
                logger.info(f"Processed tick: {command.gathering}; result: {command}")

        for command in commands.values():
            command.execute_telegram_commands()
            self._gatherings.save(command.gathering)

    def _handle_command(self, message: Message, text: str) -> Command:
        try:
            command = parse_command(text, True)
        except ParseException as e:
            return self._handle_invalid(message.chat.id, message.message_id, text)

        if command.action == 'help':
            return self._handle_help(message.chat.id, message.message_id)
        elif command.action == 'schedule' or command.action == 'plan':
            return self._handle_schedule(message.chat.id, message.message_id, command.arguments)
        elif command.action == 'start':
            return self._handle_start(message.chat.id, message.message_id, message.reply_to_message.message_id)
        elif command.action == 'stop':
            return self._handle_stop(message.chat.id, message.message_id, message.reply_to_message.message_id)
        elif command.action == 'cancel':
            return self._handle_cancel(message.chat.id, message.message_id, message.reply_to_message.message_id)
        elif command.action == 'edit':
            return self._handle_edit(message.chat.id, message.message_id, message.reply_to_message.message_id, command.arguments)
        else:
            return self._handle_unknown(message.chat.id, message.message_id, command.action)
    
    def _handle_help(self, chat_id: str, message_id: int) -> Command:
        """Handle a help command

        Actions on success:
        - send a "help" message.

        :parameter chat_id: id of the chat where the command was sent
        :parameter message_id: id of the message with the command
        """

        command = Command()
        
        command.add_telegram_command(self._new_send_message_command(chat_id, message_id, self._i18n.HELP))
        
        return command
    
    def _handle_schedule(self, chat_id: str, message_id: int, arguments: dict) -> Command:
        """Handle a schedule command

        Actions on success:
        - send a "gathering created" message;
        - pin that message;
        - create a gathering for the datasource.

        :parameter chat_id: id of the chat where the command was sent
        :parameter message_id: id of the message with the command
        :parameter arguments: arguments of the command
        """

        command = Command()

        start = arguments.get('start')
        start = self._time_parser.parse_datetime(start) if start is not None else self._time_parser.now()
        end = self._time_parser.parse_datetime(arguments.get('end'))
        max = int(arguments.get('max', '6'))
        what = arguments.get('what')
        where = arguments.get('where')
        when = arguments.get('when')

        error_messages = []
        if what is None:
            error_messages.append(self._i18n.NO_SUBJECT)
        if start < self._time_parser.now():
            error_messages.append(self._i18n.START_TIME_IN_PAST)
        if end is not None and end < self._time_parser.now():
            error_messages.append(self._i18n.END_TIME_IN_PAST)
        if end is not None and end < start:
            error_messages.append(self._i18n.END_TIME_EARLIER_THAN_START)
        if max <= 0:
            error_messages.append(self._i18n.NO_PARTICIPANTS)
            
        if len(error_messages) == 0:
            command.add_telegram_command(self._new_send_message_command(chat_id, message_id, self._i18n.CREATED.format(what, self._time_parser.format(start)), None, True))
            command.add_telegram_command(self._new_pin_message_command(chat_id))

            gathering = Gathering()
            gathering.id = self._settings.next_gathering_id()
            gathering.chat_id = chat_id
            gathering.state = STATE_SCHEDULED
            gathering.start = start
            gathering.end = end
            gathering.max_count = max
            gathering.message_what = what
            gathering.message_where = where
            gathering.message_when = when
            command.gathering = gathering
        else:
            command.add_telegram_command(self._new_send_message_command(chat_id, message_id, self._i18n.NOT_CREATED.format("\n".join(error_messages))))
        
        return command

    def _handle_start(self, chat_id: str, message_id: int, reply_to_message_id: int) -> Command:
        """Handle a start command

        Actions on success:
        - edit the gathering in the datasource.

        :parameter chat_id: id of the chat where the command was sent
        :parameter message_id: id of the message with the command
        :parameter reply_to_message_id: id of the message being replied to (should be the "Gathering created" message)
        """

        command = Command()

        if reply_to_message_id is None:
            command.add_telegram_command(self._new_send_message_command(chat_id, message_id, self._i18n.NEED_TO_REPLY_CREATED))
        else:
            gathering = self._gatherings.get_by_message_id(reply_to_message_id)
            if gathering is None:
                command.add_telegram_command(self._new_send_message_command(chat_id, message_id, self._i18n.NO_GATHERING))
            else:
                gathering.start = self._time_parser.now()
                command.gathering = gathering

        return command

    def _handle_stop(self, chat_id: str, message_id: int, reply_to_message_id: int) -> Command:
        """Handle a stop command

        Actions on success:
        - edit the gathering in the datasource.

        :parameter chat_id: id of the chat where the command was sent
        :parameter message_id: id of the message with the command
        :parameter reply_to_message_id: id of the message being replied to (should be the gathering poll message)
        """

        command = Command()

        if reply_to_message_id is None:
            command.add_telegram_command(self._new_send_message_command(chat_id, message_id, self._i18n.NEED_TO_REPLY_GATHERING))
        else:
            gathering = self._gatherings.get_by_message_id(reply_to_message_id)
            if gathering is None:
                command.add_telegram_command(self._new_send_message_command(chat_id, message_id, self._i18n.NO_GATHERING))
            else:
                gathering.end = self._time_parser.now()
                command.gathering = gathering

        return command

    def _handle_cancel(self, chat_id: str, message_id: int, reply_to_message_id: int) -> Command:
        """Handle a cancel command

        Actions on success:
        - send a "gathering cancelled" message;
        - edit the gathering in the datasource.

        :parameter chat_id: id of the chat where the command was sent
        :parameter message_id: id of the message with the command
        :parameter reply_to_message_id: id of the message being replied to (should be the "Gathering created" message or the gathering poll message)
        """

        command = Command()

        if reply_to_message_id is None:
            command.add_telegram_command(self._new_send_message_command(chat_id, message_id, self._i18n.NEED_TO_REPLY_GATHERING))
        else:
            gathering = self._gatherings.get_by_message_id(reply_to_message_id)
            if gathering is None:
                command.add_telegram_command(self._new_send_message_command(chat_id, message_id, self._i18n.NO_GATHERING))
            else:
                command.add_telegram_command(self._new_send_message_command(chat_id, message_id, self._i18n.CANCELLED.format(gathering.message_what)))

                gathering.state = STATE_STOPPED
                command.gathering = gathering

        return command

    def _handle_edit(self, chat_id: str, message_id: int, reply_to_message_id: int, arguments: dict) -> Command:
        """Handle an edit command

        Actions on success:
        - edit the poll if a running poll is edited;
        - send a "gathering edited" message;
        - edit the gathering in the datasource.

        :parameter chat_id: id of the chat where the command was sent
        :parameter message_id: id of the message with the command
        :parameter reply_to_message_id: id of the message being replied to (should be the "Gathering created" message or the gathering poll message)
        :parameter arguments: arguments of the command
        """

        command = Command()

        if reply_to_message_id is None:
            command.add_telegram_command(self._new_send_message_command(chat_id, message_id, self._i18n.NEED_TO_REPLY_CREATED_OR_GATHERING))
        else:
            gathering = self._gatherings.get_by_message_id(reply_to_message_id)
            if gathering is None:
                command.add_telegram_command(self._new_send_message_command(chat_id, message_id, self._i18n.NO_GATHERING))
            else:
                edited_messages = []
                error_messages = []

                start = arguments.get('start')
                if start is not None:
                    start = self._time_parser.parse_datetime(start)
                    if gathering.start != start:
                        if start < self._time_parser.now():
                            error_messages.append(self._i18n.START_TIME_IN_PAST)
                        else:
                            gathering.start = start
                            edited_messages.append(self._i18n.EDITED_START.format(self._time_parser.format(gathering.start)))

                end = arguments.get('end')
                if end is not None:
                    end = self._time_parser.parse_datetime(end)
                    if gathering.end != end:
                        if end < self._time_parser.now():
                            error_messages.append(self._i18n.END_TIME_IN_PAST)
                        elif start is not None and end < start:
                            error_messages.append(self._i18n.END_TIME_EARLIER_THAN_START)
                        else:
                            gathering.end = end
                            edited_messages.append(self._i18n.EDITED_END.format(self._time_parser.format(gathering.end)))
                            
                max = arguments.get('max')
                if max is not None:
                    max = int(max)
                    if gathering.max_count != max:
                        if max <= 0:
                            error_messages.append(self._i18n.NO_PARTICIPANTS)
                        else:
                            gathering.max_count = max
                            edited_messages.append(self._i18n.EDITED_MAX.format(gathering.max_count))
                            
                what = arguments.get('what')
                if what is not None and gathering.message_what != what:
                    gathering.message_what = what
                    edited_messages.append(self._i18n.EDITED_WHAT.format(gathering.message_what))
                            
                where = arguments.get('where')
                if where is not None and gathering.message_where != where:
                    gathering.message_where = where
                    edited_messages.append(self._i18n.EDITED_WHERE.format(gathering.message_where))
                            
                when = arguments.get('when')
                if when is not None and gathering.message_when != when:
                    gathering.message_when = when
                    edited_messages.append(self._i18n.EDITED_WHEN.format(gathering.message_when))

                if len(error_messages) == 0:
                    if len(edited_messages) == 0:
                        command.add_telegram_command(self._new_send_message_command(chat_id, message_id, self._i18n.NOT_EDITED.format(gathering.message_what, self._i18n.NO_EDITS)))
                    else:
                        if gathering.state == STATE_STARTED:
                            command.add_telegram_command(self._new_edit_message_command(gathering.chat_id, gathering.message_id, self._build_poll_message_text(gathering), self._build_poll_message_keyboard()))
                        command.add_telegram_command(self._new_send_message_command(chat_id, message_id, self._i18n.EDITED.format(gathering.message_what, "\n".join(edited_messages))))
                        command.gathering = gathering
                else:
                    command.add_telegram_command(self._new_send_message_command(chat_id, message_id,self._i18n.NOT_EDITED.format(gathering.message_what, "\n".join(error_messages))))

        return command

    def _handle_unknown(self, chat_id: str, message_id: int, cmd: str) -> Command:
        command = Command()

        command.add_telegram_command(self._new_send_message_command(chat_id, message_id, self._i18n.UNKNOWN_COMMAND.format(cmd)))

        return command

    def _handle_invalid(self, chat_id: str, message_id: int, cmd: str) -> Command:
        command = Command()

        command.add_telegram_command(self._new_send_message_command(chat_id, message_id, self._i18n.INVALID_COMMAND.format(cmd)))

        return command

    def _handle_callback(self, callback_query: CallbackQuery) -> Command:
        """Handle a callback

        Actions on success:
        - edit the poll;
        - edit the gathering in the datasource.

        :parameter callback_query: the callback query obtained from Telegram
        """

        command = Command()

        chat_id = callback_query.message.chat.id
        message_id = callback_query.message.message_id
        gathering = self._gatherings.get_by_message_id(message_id)
        if gathering is None:
            command.add_telegram_command(self._new_send_message_command(chat_id, message_id, self._i18n.NO_GATHERING))
        elif gathering.state != STATE_STARTED:
            command.add_telegram_command(self._new_send_message_command(chat_id, message_id, self._i18n.GATHERING_NOT_RUNNING))
        else:
            name = callback_query.from_user.name()
            data = callback_query.data
            if data == 'yes':
                if len(gathering.participants_yes) < gathering.max_count:
                    gathering.participants_yes.add(name)
                    gathering.participants_maybe.discard(name)
                    gathering.participants_no.discard(name)
            elif data == 'maybe':
                gathering.participants_yes.discard(name)
                gathering.participants_maybe.add(name)
                gathering.participants_no.discard(name)
            elif data == 'no':
                gathering.participants_yes.discard(name)
                gathering.participants_maybe.discard(name)
                gathering.participants_no.add(name)
            elif data == 'remove':
                gathering.participants_yes.discard(name)
                gathering.participants_maybe.discard(name)
                gathering.participants_no.discard(name)
            else:
                gathering = None
                command.add_telegram_command(self._new_send_message_command(chat_id, message_id, self._i18n.UNKNOWN_COMMAND.format(data)))

            if gathering is not None:
                command.add_telegram_command(self._new_edit_message_command(gathering.chat_id, gathering.message_id, self._build_poll_message_text(gathering), self._build_poll_message_keyboard()))
                command.gathering = gathering

        return command

    def _handle_tick(self, gathering: Gathering) -> Command | None:
        if gathering.state == STATE_SCHEDULED and self._time_parser.now() >= gathering.start:
            return self._handle_tick_start(gathering)
        elif gathering.state == STATE_STARTED and gathering.end is not None and self._time_parser.now() >= gathering.end:
            return self._handle_tick_end(gathering)
        else:
            return None

    def _handle_tick_start(self, gathering: Gathering) -> Command:
        command = Command()

        if gathering.message_id is not None:
            command.add_telegram_command(self._new_unpin_message_command(gathering.chat_id, gathering.message_id))
        command.add_telegram_command(self._new_send_message_command(gathering.chat_id, None, self._build_poll_message_text(gathering), self._build_poll_message_keyboard(), True))
        command.add_telegram_command(self._new_pin_message_command(gathering.chat_id))

        gathering.state = STATE_STARTED
        command.gathering = gathering

        return command

    def _handle_tick_end(self, gathering: Gathering) -> Command:
        command = Command()

        command.add_telegram_command(self._new_edit_message_command(gathering.chat_id, gathering.message_id, self._build_poll_message_text(gathering)))
        command.add_telegram_command(self._new_unpin_message_command(gathering.chat_id, gathering.message_id))

        min_legionnaires = max(0, gathering.max_count - len(gathering.participants_yes) - len(gathering.participants_maybe))
        max_legionnaires = gathering.max_count - len(gathering.participants_yes)
        if min_legionnaires == 1 and max_legionnaires == 1:
            legionnaires = self._i18n.POLL_RESULT_LEGIONNAIRES_ONE
        elif (min_legionnaires > 1 or max_legionnaires > 1) and min_legionnaires == max_legionnaires:
            legionnaires = self._i18n.POLL_RESULT_LEGIONNAIRES_MANY.format(min_legionnaires)
        elif (min_legionnaires > 1 or max_legionnaires > 1) and min_legionnaires != max_legionnaires:
            legionnaires = self._i18n.POLL_RESULT_LEGIONNAIRES_MANY.format(f"{min_legionnaires}-{max_legionnaires}")
        else:
            legionnaires = ""

        command.add_telegram_command(self._new_send_message_command(gathering.chat_id, gathering.message_id, self._i18n.POLL_RESULT.format(
            what=gathering.message_what,
            where=self._i18n.POLL_WHERE.format(gathering.message_where) if gathering.message_where is not None else "",
            when=self._i18n.POLL_WHEN.format(gathering.message_when) if gathering.message_when is not None else "",
            max_count=gathering.max_count,
            participants_yes=self._join_names(gathering.participants_yes),
            participants_maybe=self._join_names(gathering.participants_maybe),
            participants_no=self._join_names(gathering.participants_no),
            legionnaires=legionnaires
        )))

        gathering.state = STATE_STOPPED
        command.gathering = gathering

        return command

    def _new_send_message_command(self, chat_id: str, message_id: int, text: str, reply_markup: InlineKeyboardMarkup = None, is_updating: bool = False) -> AbstractTelegramCommand:
        return SendMessageCommand(
            self._telegram,
            self._i18n,
            SendMessageRequest(
                chat_id=chat_id,
                text=text,
                parse_mode=MODE_HTML,
                reply_markup=reply_markup,
                reply_to_message_id=message_id,
            ),
            is_updating
        )

    def _new_edit_message_command(self, chat_id: str, message_id: int, text: str, reply_markup: InlineKeyboardMarkup = None) -> AbstractTelegramCommand:
        return EditMessageCommand(
            self._telegram,
            self._i18n,
            EditMessageRequest(
                chat_id=chat_id,
                message_id=message_id,
                text=text,
                parse_mode=MODE_HTML,
                reply_markup=reply_markup,
            )
        )

    def _new_pin_message_command(self, chat_id: str, message_id: int = None) -> AbstractTelegramCommand:
        return PinMessageCommand(self._telegram, self._i18n, chat_id, message_id)

    def _new_unpin_message_command(self, chat_id: str, message_id: int) -> AbstractTelegramCommand:
        return UnpinMessageCommand(self._telegram, self._i18n, chat_id, message_id)

    def _join_names(self, names: set[str]) -> str:
        return "\n" + "\n".join(names) if len(names) != 0 else ""

    def _build_poll_message_text(self, gathering: Gathering) -> str:
        return self._i18n.POLL.format(
            what=gathering.message_what,
            where=self._i18n.POLL_WHERE.format(gathering.message_where) if gathering.message_where is not None else "",
            when=self._i18n.POLL_WHEN.format(gathering.message_when) if gathering.message_when is not None else "",
            max_count=gathering.max_count,
            end=self._i18n.POLL_UNTIL.format(self._time_parser.format(gathering.end)) if gathering.end is not None else "",
            participants_yes=self._join_names(gathering.participants_yes),
            participants_maybe=self._join_names(gathering.participants_maybe),
            participants_no=self._join_names(gathering.participants_no),
        )

    def _build_poll_message_keyboard(self) -> InlineKeyboardMarkup:
        return InlineKeyboard() \
            .add_row() \
            .add_button(self._i18n.BUTTON_YES, "yes") \
            .add_button(self._i18n.BUTTON_MAYBE, "maybe") \
            .add_row() \
            .add_button(self._i18n.BUTTON_NO, "no") \
            .add_button(self._i18n.BUTTON_REMOVE, "remove") \
            .to_telegram_model()
