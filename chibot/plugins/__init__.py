"""
Chibot plugins.
"""

__all__ = [
    'http',
    'logs',
    'help',
]


registered_plugins = {}


NO_RESPONSE = 0
NORMAL_RESPONSE = 1
NOTICE_RESPONSE = 2


class Response(object):
    """
    A plugin response. All plugins should return an instance 
    of this class, or a subclass.
    """
    def __init__(self, content, response_type=None):
        """
        :param content: an iterable of lines to be output
        :param response_type: the response type integer
        """
        if isinstance(content, basestring):
            self._content = [content]
        else:
            self._content = content

        self._response_type = response_type

    def __iter__(self):
        return iter(self._content)

    def __str__(self):
        return '\n'.join(self._content)

    def __repr__(self):
        return '\n'.join(self._content)

    @property
    def content(self):
        return self._content

    @property
    def response_type(self):
        return self._response_type


class NoticeResponse(Response):
    """
    A response with type NOTICE_RESPONSE.
    """
    def __init__(self, content):
        super(NoticeResponse, self).__init__(content, NOTICE_RESPONSE)


def register(name=None, response_type=NORMAL_RESPONSE):
    """
    Function to register a plugin.
    """
    def decorator(f):
        def wrapper(*args, **kwargs):
            resp = f(*args, **kwargs)
            
            if isinstance(resp, basestring):
                # Plugin returned a string
                resp = Response((resp,))

            if isinstance(resp, tuple) or isinstance(resp, list):
                # Plugin returned an iterable
                resp = Response(resp)

            if resp.response_type is None:
                # No response type specified, so use default
                resp = Response(resp.content, response_type)

            return resp

        # Set help text
        wrapper.__doc__ = f.__doc__

        # Register the plugin
        if name is None:
            plugin_name = f.func_name
        else:
            plugin_name = name

        registered_plugins[plugin_name] = wrapper

        return wrapper

    return decorator


