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


class LogEntryPlugin(plugins.Plugin):
    _name = None

    def _message_filter(self, message):
        return message.public

    def run(self, message):
        entry = connection.chibot.log.LogEntry()
        entry['nickname'] = message.nickname
        entry['username'] = message.user
        entry['host'] = message.host
        entry['message'] = message.content
        entry['timestamp'] = datetime.datetime.now()
        entry.save()
        return None

plugins.register(LogEntryPlugin())


class NickStatsPlugin(plugins.Plugin):
    _name = 'nickstats'
    _arguments = (
        ('nick', 'tok', None),
    )
    _response_class = plugins.NoticeResponse

    def run(self, nick, **kwargs):
        resp = []

        resp.append('Nickname: %s' % nick)

        # Hit the DB
        cursor = connection.chibot.log.LogEntry.find({'nickname': nick})

        # Compile some stats
        if cursor.count() > 0:
            resp.append('Number of messages: %s' % cursor.count())
            resp.append('Time of last message: %s' % cursor.sort('timestamp', -1)[0]['timestamp'])
            resp.append('Last message: %s' % cursor.sort('timestamp', -1)[0]['message'])
        else:
            resp.append('No such user found.')

        return resp

plugins.register(NickStatsPlugin())
