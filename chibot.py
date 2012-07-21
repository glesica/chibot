#!/usr/bin/env python
import sys
import argparse
import chibot

parser = argparse.ArgumentParser(
    description='Run Chibot.'
)
parser.add_argument(
    '--plugins',
    dest='plugins',
    metavar='P',
    type=str,
    nargs='*',
    default=(),
    help='User-defined plugins to import. Given as Python modules.'
)
parser.add_argument(
    '--server',
    dest='server',
    type=str,
    required=True,
    help='Server to connect to.'
)
parser.add_argument(
    '--channel',
    dest='channel',
    required=True,
    help='Channel to connect to.'
)
parser.add_argument(
    '--nickname',
    dest='nickname',
    required=True,
    help='Nickname to use.'
)
parser.add_argument(
    '--port',
    dest='port',
    type=int,
    default=6667,
    help='Port number to connect to.'
)

args = parser.parse_args()

# Import plugins specified on the command line
for plugin in args.plugins:
    if '.' in plugin:
        pkg, mod = plugin.rsplit('.', 1)
    else:
        pkg = plugin
        mod = ''
    __import__(pkg, fromlist=[mod])

# Connect and start listening
bot = chibot.bot.ChiBot(
    channel=args.channel,
    nickname=args.nickname,
    server=args.server,
    port=args.port,
    plugins=chibot.plugins.registered_plugins,
)
bot.start()
