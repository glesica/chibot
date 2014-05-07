"""
Classes and functions related to incoming IRC messages.
"""

class Message(object):
    """
    An incoming IRC message.
    """
    def __init__(self, event, public):
        self.public = public
        self.nickname = event.source().nick
        self.content = event.arguments()[0]
        self.user = event.source().user[0]
        self.host = event.source().host
        self.target = event.target()
 
