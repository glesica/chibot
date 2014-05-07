"""
ChiBot command to return the HTTP status code for a URL 
given as an argument.
"""
import requests
from chibot import plugins


MAX_URLS = 10


class HTTPStatusPlugin(plugins.Plugin):
    _name = 'httpstatus'
    _arguments = (
        ('urls', ('tok',), None),
    )
    _response_class = plugins.NoticeResponse

    def run(self, urls, **kwargs):
        if not urls:
            return 'Provide one or more URLS'

        resp = []
        if len(urls) > MAX_URLS:
            resp.append('Processing first %s URLS' % MAX_URLS)

        for u in urls[:MAX_URLS]:
            code = requests.get(u).status_code
            resp.append('%s ... %s' % (u, code))

        return resp

plugins.register(HTTPStatusPlugin())
