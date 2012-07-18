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


def create_entry(nick, user, host, msg):
    entry = connection.chibot.log.LogEntry()
    entry['nickname'] = nick
    entry['username'] = user
    entry['host'] = host
    entry['message'] = msg
    entry['timestamp'] = datetime.datetime.now()
    entry.save()


def search(cmd, *terms, **kwargs):
    """
    Usage: logs.search <terms>. Searches the chat log for the given terms.
    """
    return ' '.join(terms)


@plugins.register(response_type=plugins.NOTICE_RESPONSE)
def search_nick(cmd, *args, **kwargs):
    """
    Usage: logs.search_nick <nick>. Displays some nifty stats about a given nickname.
    """
    resp = []

    if not args:
        return 'Need a nickname to search for.'

    if len(args) > 1:
        resp.append('Too many nicknames, skipping all but the first.')

    nickname = args[0]
    print nickname #DEBUG
    resp.append('Nickname: %s' % nickname)

    # Hit the DB
    cursor = connection.chibot.log.LogEntry.find({'nickname': nickname})

    print cursor #DEBUG
    print cursor.count() #DEBUG
    # Compile some stats
    resp.append('Number of entries: %s' % cursor.count())

    return resp




