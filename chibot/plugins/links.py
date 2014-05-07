"""
URL plugin for Chibot.
"""
import datetime
import mongokit
from chibot import plugins
from chibot import urlwrangler


connection = mongokit.Connection()


@connection.register
class LinkMeta(mongokit.Document):
    """
    Meta data for the link DB.
    """
    __collection__ = 'links_meta'

    structure = {
        'counter': int
    }
    required_fields = ['counter']
    default_values = {
        'counter': 0,
    }


@connection.register
class Link(mongokit.Document):
    __collection__ = 'links'

    structure = {
        'id': int,
        'timestamp': datetime.datetime,
        'nickname': basestring,
        'username': basestring,
        'host': basestring,
        'url': basestring,
        'title': basestring,
        'comments': {
            'timestamp': datetime.datetime,
            'nickname': basestring,
            'username': basestring,
            'host': basestring,
            'content': basestring,
        },
        'score': int,
    }
    required_fields = ['id', 'timestamp', 'nickname', 'url']
    default_values = {
        'score': 0,
    }
    indexes = [
        {
            'fields': ['id'],
            'unique': True,
        },
        {
            'fields': ['timestamp'],
        },
        {
            'fields': ['nickname'],
        },
    ]


class URLIndexPlugin(plugins.Plugin):
    _name = 'urlindex'
    _response_class = plugins.NoticeResponse

    def _message_filter(self, message):
        urls = urlwrangler.get_urls(message.content)
        return bool(urls)

    def run(self, message, **kwargs):
        urls = urlwrangler.get_urls(message.content)
        resp = []

        for u in urls:
            meta = connection.chibot.links_meta.find_and_modify(
                {},
                {'$inc': {'counter': 1}},
                new=True
            )
            link = connection.chibot.Link()
            link['id'] = int(meta['counter'])
            link['timestamp'] = datetime.datetime.now()
            link['nickname'] = message.nickname
            link['username'] = message.user
            link['host'] = message.host
            link['url'] = u
            link.save()

            resp.append('%s: %s' % (link['id'], link['url']))
        
        return resp

plugins.register(URLIndexPlugin())
   

class URLTitlePlugin(plugins.Plugin):
    _name = 'urltitle'
    _arguments = (
        ('url_id', int, None),
        ('title', str, None),
    )
    _response_class = plugins.NoticeResponse

    def run(self, url_id, title, **kwargs):
        resp = []
        resp.append('%s' % url_id)
        resp.append(title)

plugins.register(URLTitlePlugin())
