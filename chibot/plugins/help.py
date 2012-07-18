"""
Chibot help system.
"""
from chibot import plugins


MAX_CHARACTERS = 250


@plugins.register(response_type=plugins.NOTICE_RESPONSE)
def help(cmd, *args, **kwargs):
    """
    Usage: status_code <urls...>. Attempts a GET request to the given URL and returns the HTTP status code received.
    """
    resp = []

    if not args:
        for name, func in plugins.registered_plugins.items():
            resp.append('%s' % name)
    else:
        for name, func in plugins.registered_plugins.items():
            if name in args:
                if func.__doc__:
                    resp.append('%s: %s' % (name, func.__doc__.replace('\n', '')[:MAX_CHARACTERS]))
                else:
                    resp.append('%s: %s' % (name, 'No help available'))

    return resp




