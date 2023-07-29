HELP  = """
Team Gather Bot - bot to simplify gathering a team for an event.

Available commands:
* <b>help</b> - this help.

* <b>schedule</b> or <b>plan</b> - schedule a gather, parameters (all parameters are optional unless stated otherwise):
  - <i>start</i>: gather start time in <code>[[[YYYY-]MM-]DD'T']HH[:mm[:ss]]</code> format
    where missing date parts are equal to the ones of today, missing time parts are equal to zero,
    by default the gathering starts at the time of schedule message being sent;
  - <i>end</i>: gather end time in the same format, only manual end by default;
  - <i>max</i>: the maximum number of participants, 6 by default;
  - <i>what</i>: event name, a required parameter;
  - <i>where</i>: event place, empty by default;
  - <i>when</i>: event time, empty by default.

* <b>start</b> - manual gathering start, this command should be sent in response to the gathering schedule message.

* <b>end</b> - manual gathering end, this command should be sent in response to the gathering poll.

* <b>cancel</b> - gathering cancellation, this command should be sent in response either to the gathering schedule message or to the gathering poll.

* <b>edit</b> - gathering edit, accepts the same parameters as <b>schedule</b>.

Upon reaching the gathering end time or receiving the <b>end</b> command, the gathering poll is closed and the results message is sent.

<i><a href="https://github.com/hamsterxc/team_gather_bot">Source code</a>.</i>
""".strip()

NOT_CREATED = "<i>Gathering not created.</i>\n{0}"
NOT_EDITED = "<i>Gathering \"<b>{0}</b>\" not changed.</i>\n{1}"
START_TIME_IN_PAST = "- <i>Start time is already in the past.</i>"
END_TIME_IN_PAST = "- <i>End time is already in the past.</i>"
END_TIME_EARLIER_THAN_START = "- <i>End time is earlier than start time.</i>"
NO_PARTICIPANTS = "- <i>No participants planned.</i>"
NO_SUBJECT = "- <i>Gathering subject not set.</i>"
NO_EDITS = "<i>No gathering edits.</i>"

NEED_TO_REPLY_CREATED = "<i>The command must be executed as a reply to the message about gathering creation.</i>"
NEED_TO_REPLY_GATHERING = "<i>The command must be executed as a reply to the gathering message.</i>"
NEED_TO_REPLY_CREATED_OR_GATHERING = "<i>The command must be executed as a reply to the message about gathering creation or to the gathering message.</i>"
NO_GATHERING = "<i>Gathering not found.</i>"
GATHERING_NOT_RUNNING = "<i>Gathering is not running.</i>"

CREATED = "Gathering \"<b>{0}</b>\" created. Starts <b>{1}</b>."
CANCELLED = "Gathering \"<b>{0}</b>\" cancelled."

EDITED = "Gathering \"<b>{0}</b>\" changed:\n{1}"
EDITED_START = "- New start: {0}"
EDITED_END = "- New end: {0}"
EDITED_MAX = "- New participants count: {0}"
EDITED_WHAT = "- New subject: {0}"
EDITED_WHERE = "- New place: {0}"
EDITED_WHEN = "- New time: {0}"

BUTTON_YES = "\u2705 I will be"
BUTTON_MAYBE = "\u2753 Maybe"
BUTTON_NO = "\ud83d\udeab I won't be"
BUTTON_REMOVE = "\u274c Remove my answer"
POLL = """
What: <b>{what}</b>{where}{when}
Participants: <b>{max_count}</b>{end}

\u2705 <b>Will be</b>:{participants_yes}

\u2753 <b>Maybe</b>:{participants_maybe}

\ud83d\udeab <b>Won't be</b>:{participants_no}
""".strip()
POLL_WHERE = "\nWhere: <b>{0}</b>"
POLL_WHEN = "\nWhen: <b>{0}</b>"
POLL_UNTIL = "\nGathering until: <b>{0}</b>"

POLL_RESULT = """
What: <b>{what}</b>{where}{when}
Participants: <b>{max_count}</b>

\u2705 <b>Will be</b>:{participants_yes}

\u2753 <b>Maybe</b>:{participants_maybe}

\ud83d\udeab <b>Won't be</b>:{participants_no}

{legionnaires}
""".strip()
POLL_RESULT_LEGIONNAIRES_ONE = "<b>One</b> more legionnaire might be needed."
POLL_RESULT_LEGIONNAIRES_MANY = "<b>{0}</b> more legionnaires might be needed."

TELEGRAM_ERROR = "<i>Telegram error occurred: {0}\n{1}</i>"
UNKNOWN_COMMAND = "<i>Unknown command: {0}.</i>"
INVALID_COMMAND = "<i>Invalid command: \"{0}\".</i>"
