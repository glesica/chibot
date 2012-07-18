#!/usr/bin/env python
import sys, argparse
import chibot

parser = argparse.ArgumentParser(
    description='Run Chibot.'
)
parser.add_argument(
    '--commands',
    dest='commands',
    metavar='C',
    type=str,
    nargs='*',
    default=(),
    help='User-defined commands to import.'
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

# Load plugins
found_plugins = {}

# Built-in
found_plugins.update(chibot.plugins.registered_plugins)

# Defined in CWD
pass

# Passed on command line
pass

# Connect and start listening
bot = chibot.bot.ChiBot(
    channel=args.channel, 
    nickname=args.nickname, 
    server=args.server, 
    port=args.port, 
    plugins=found_plugins,
)
bot.start()


