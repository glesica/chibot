from . import plugins
from . import bot

# Loads the built-in plugins
from .plugins import *


# class Message(object):
#     """
#     An incoming IRC message.
#     """
#     def __init__(self, event, public):
#         self.public = public
#         self.nickname = event.source().nick
#         self.content = even.arguments()[0]
#         self.user = event.source().user[0]
#         self.host = event.source().host
