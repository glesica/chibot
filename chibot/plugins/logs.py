"""
Logging plugins and tools.
"""
import datetime
import mongokit
from chibot import plugins


connection = mongokit.Connection()


@connection.register
class LogEntry(mongokit.Document):
    structure = {
        'timestamp': datetime.datetime,
        'nickname': basestring,
        'username': basestring,
        'host': basestring,
        'message': basestring,
    }
    required_fields = ['timestamp', 'nickname']
    indexes = [
        {
            'fields': ['timestamp'],
        },
        {
            'fields': ['nickname'],
        },
    ]


def create_entry(event):
    nick = event.source().nick
    user = event.source().user[0]
    host = event.source().host
    msg = event.arguments()[0]

    entry = connection.chibot.log.LogEntry()
    entry['nickname'] = nick
    entry['username'] = user
    entry['host'] = host
    entry['message'] = msg
    entry['timestamp'] = datetime.datetime.now()
    entry.save()


def log_stats(cmd, *args, **kwargs):
    """
    Usage: logs.search <terms>. Searches the chat log for the given terms.
    """
    pass


@plugins.register(response_type=plugins.NOTICE_RESPONSE)
def nick_stats(cmd, *args, **kwargs):
    """
    Usage: nick_stats <nick>. Displays some nifty stats about a given nickname.
    """
    resp = []

    if not args:
        return 'Need a nickname to search for.'

    if len(args) > 1:
        resp.append('Too many nicknames, skipping all but the first.')

    nickname = args[0]
    resp.append('Nickname: %s' % nickname)

    # Hit the DB
    cursor = connection.chibot.log.LogEntry.find(
        {
            'nickname': nickname,
        }
    )

    # Compile some stats
    if cursor.count() > 0:
        resp.append('Number of messages: %s' % cursor.count())
        resp.append('Time of last message: %s' % cursor.sort('timestamp')[0]['timestamp'])
        resp.append('Last message: %s' % cursor.sort('timestamp')[0]['message'])
    else:
        resp.append('No such user found.')

    return resp




