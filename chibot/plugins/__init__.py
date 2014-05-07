"""
Chibot plugins.
"""

__all__ = [
    'http',
    'logs',
    'links',
    #'help',
]


registered_plugins = []


NO_RESPONSE = 0
NORMAL_RESPONSE = 1
NOTICE_RESPONSE = 2


class PluginError(Exception):
    pass


# ------------------------------------------------------------------------------
# Responses
# ------------------------------------------------------------------------------


class Response(object):
    """
    A plugin response. All plugins should return an instance 
    of this class, or a subclass.
    """
    def __init__(self, content, target=None, response_type=NO_RESPONSE):
        """
        :param content: an iterable of lines to be output or a string 
            which will be broken into lines at '\n' characters.
        :param response_type: the response type integer
        """
        #TODO: Better error handling
        if isinstance(content, basestring):
            self._content = tuple(content.split('\n'))
        else:
            self._content = tuple(content)

        self._target = target
        self._response_type = response_type

    def __iter__(self):
        return iter(self._content)

    def __str__(self):
        return '\n'.join(self._content)

    def __repr__(self):
        return '\n'.join(self._content)

    @property
    def content(self):
        return self._content[:]

    @property
    def target(self):
        return self._target

    @property
    def response_type(self):
        return self._response_type


class NormalResponse(Response):
    """
    A response with type NORMAL_RESPONSE.
    """
    def __init__(self, content, target):
        super(NormalResponse, self).__init__(content, target, NORMAL_RESPONSE)


class NoticeResponse(Response):
    """
    A response with type NOTICE_RESPONSE.
    """
    def __init__(self, content, target):
        super(NoticeResponse, self).__init__(content, target, NOTICE_RESPONSE)


# ------------------------------------------------------------------------------
# Plugins
# ------------------------------------------------------------------------------


def register(plugin):
    registered_plugins.append(plugin)


class Plugin(object):
    """
    A Chibot plugin. This should be used as a base-class for 
    creating additional plugins.

    The following attributes can/should be overridden in sub-
    classes:

    ``name``: name of the plugin. This can be set in the ``__init__`` 
        method if multiple instances will be used. Set to ``None`` 
        for plugins that do not have associated commands.
    ``arguments``: list of arguments accepted by the plugin
    ``message_filter``: a boolean function that accepts a 
        ``Message`` object. The plugin will abort if the function 
        returns ``False``.
    ``response_type``: the default ``Response`` sub-class to use 
        for this plugin.
    """
    _name = None
    _arguments = ()
    _response_class = Response
    
    def __init__(self, name=None):
        if name:
            self._name = name.replace(' ', '_')

    def __call__(self, message):
        """
        Process the given message and return the output as an 
        instance of ``Response`` (or a sub-class). Will 
        return ``None`` if no action was necessary on the part 
        of this plugin.
        """
        if not self._message_filter(message):
            return None

        # Parse and augment the arguments
        if self._arguments:
            args, kwargs = self._parse_arguments(message)
        else:
            args = []
            kwargs = {}
        kwargs['message'] = message

        # Attempt to run the plugin
        try:
            resp = self.run(*args, **kwargs)
        except PluginError, e:
            resp = '%s: Error: %s' % (self._name, e)
        except Exception, e:
            resp = '%s: Error: %s' % (self._name, e)

        # Ensure there is no output if None came back
        if resp is None:
            return Response('')

        # Figure out where the response should be directed
        if message.public:
            target = message.target
        else:
            target = message.nickname

        return self._response_class(resp, target)

    @staticmethod
    def _parse_str(tokens):
        """
        Parses string arguments.

        >>> tokens = ['hello', 'there', 'guy']
        >>> Plugin._parse_str(tokens)
        'hello there guy'
        >>> tokens
        []

        >>> tokens = ['"hello', 'there"', 'guy']
        >>> Plugin._parse_str(tokens)
        'hello there'
        >>> tokens
        ['guy']

        >>> tokens = ['"hello', 'there"guy']
        >>> Plugin._parse_str(tokens)
        'hello there'
        >>> tokens
        ['guy']

        >>> tokens = ['"hello', 'there', '"guy']
        >>> Plugin._parse_str(tokens)
        'hello there'
        >>> tokens
        ['guy']
        
        >>> tokens = ['"hello', '"there"', 'guy']
        >>> Plugin._parse_str(tokens)
        'hello'
        >>> tokens
        ['there"', 'guy']
        """
        # A string argument is a special case, it consumes the
        # rest of the tokens unless it finds a double-quote at
        # the beginning of the next token, in which case it
        # consumes all tokens up to the next double-quote. If the
        # next double-quote occurs somewhere other than the end
        # of its token, the token is split and the part past the
        # double-quote is pushed back on to the tokens list.
        # There is no way to escape a double-quote at this time.
        quoted = tokens[0][0] == '"'

        if not quoted:
            str_tokens = tokens[:]
            del tokens[:]
            return ' '.join(str_tokens)

        # String must be quoted
        next_token = tokens.pop(0)[1:]
        str_tokens = []
        while '"' not in next_token:
            str_tokens.append(next_token)
            next_token = tokens.pop(0)

        # Split up the token and save the parts
        sp, tp = next_token.split('"', 1)
        if sp:
            str_tokens.append(sp)
        if tp:
            tokens.insert(0, tp)

        return ' '.join(str_tokens)

    @staticmethod
    def _parse_int(tokens):
        """
        Extracts a single token and parses it into an integer.
        """
        return int(tokens.pop(0))

    @staticmethod
    def _parse_float(tokens):
        """
        Extracts a single token and parses it into a float.
        """
        return float(tokens.pop(0))

    @staticmethod
    def _parse_bool(tokens):
        """
        Extracts a single token and parses it to a boolean.
        """
        next_token = tokens.pop(0)
        return not next_token.lower() in (
            'false',
            'f',
            '0',
            'off',
            'no',
        )

    @staticmethod
    def _parse_tok(tokens):
        """
        Extracts a single token and returns it as a string.
        """
        return tokens.pop(0)

    def _parse_value(self, tokens, dt):
        if dt is str:
            return self._parse_str(tokens)
        elif dt is int:
            return self._parse_int(tokens)
        elif dt is float:
            return self._parse_float(tokens)
        elif dt is bool:
            return self._parse_bool(tokens)
        elif dt == 'tok':
            return self._parse_tok(tokens)
        else:
            raise Exception('Invalid data type: %s' % dt)

    def _message_filter(self, message):
        """
        Default message filter method. Checks whether the plugin 
        has a name and, if it does, looks for a command in the 
        message of the form !<name>. This should be suitable for 
        most plugins, although some (such as for logging or 
        plugins that need to respond to normal conversation) will 
        need to override this method.
        """
        if self._name:
            cmd = '!' + self._name
            #TODO: startswith instead?
            return cmd in message.content
        return False

    def _parse_arguments(self, message):
        # Start parsing at the command
        alltokens = message.content.split(' ')
        if self._name:
            cmd_index = alltokens.index('!' + self._name)
            tokens = alltokens[cmd_index+1:]
        else:
            tokens = alltokens[:]

        args = []
        kwargs = {}
        
        # Operate on name, type and default for each
        for n, t, d in self._arguments:
            if type(t) in (list, tuple):
                single = False
                if len(t) == 0:
                    raise Exception('Empty argument list has no meaning')
                elif len(t) == 1:
                    # Consume all
                    types = t * len(tokens)
                else:
                    # Consume N
                    types = t[:]
            else:
                single = True
                types = (t,)

            try:
                argval = [self._parse_value(tokens, tp) for tp in types]
                # Convert list back to single value if needed
                if single:
                    [argval] = argval
            except IndexError, e:
                # This means tokens was empty, use default
                argval = d
            except ValueError, e:
                raise PluginError('Invalid type for %s' % n)
 
            if n:
                kwargs[n] = argval
            else:
                args.append(argval)

        return args, kwargs

    def run(self):
        """
        Default implementation does nothing. Override this method 
        in a sub-class. The method should return a ``Response`` object, 
        a string or an iterable of strings (which will become lines in 
        the output). ``None`` is also a valid return value. It will become 
        a blank response, nothing will be output.
        """
        return 'Hello, world!'
