"""
ChiBot command to return the HTTP status code for a URL 
given as an argument.
"""
import requests
from chibot import plugins


MAX_URLS = 10
COLUMN_WIDTH = 20


@plugins.register(response_type=plugins.NOTICE_RESPONSE)
def status_code(cmd, *args, **kwargs):
    """
    Usage: status_code <urls...>. Attempts a GET request to the given URL and returns the HTTP status code received.
    """
    resp = []

    if not args:
        return 'Sorry, you need to provide at least one URL.'

    if len(args) > MAX_URLS:
        resp.append('Too many URLs given. Skipping some.')

    for url in args[:MAX_URLS]:
        code = requests.get(url).status_code
        resp.append('%s | %s' % (url[:COLUMN_WIDTH], code))
        
    return resp




