"""
An IRC bot for the Chicago GLUG channel.
"""
import datetime
import irc.bot
from irc.client import irc_lower, ip_numstr_to_quad, ip_quad_to_numstr
from . import plugins


class ChiBot(irc.bot.SingleServerIRCBot):
    def __init__(self, plugins, channel, nickname, server, port=6667):
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.channel = channel
        self.plugins = plugins

    def on_nicknameinuse(self, conn, event):
        conn.nick(conn.get_nickname() + "_")

    def on_welcome(self, conn, event):
        conn.join(self.channel)

    def on_privmsg(self, conn, event):
        self._process_message(conn, event, public=False)

    def on_pubmsg(self, conn, event):
        self._process_message(conn, event, public=True)

    # Custom methods

    def _iscmd(self, msg):
        # Anything that starts with a ! will be a command 
        # for now.
        #TODO: Account for "<nick>:" at the front
        return msg.strip()[0] == '!'

    def _parse_command(self, msg):
        tokens = msg.split()
        cmd = tokens[0].lstrip('!')
        args = tokens[1:]
        return cmd, args

    def _process_cmd(self, conn, event, public, msg):
        cmd, args = self._parse_command(msg)

        try:
            func = plugins.registered_plugins[cmd]
            resp = func(cmd, *args)
        except KeyError, e:
            resp = plugins.NoticeResponse('Invalid command, use "help"...')
        except Exception, e:
            resp = plugins.NoticeResponse('Something went horribly wrong...')

        return resp

    def _send_response(self, conn, resp, target):
        for line in resp:
            if resp.response_type == plugins.NORMAL_RESPONSE:
                conn.privmsg(target, line)
            if resp.response_type == plugins.NOTICE_RESPONSE:
                conn.notice(target, line)

    def _process_message(self, conn, event, public):
        nick = event.source().nick
        user = event.source().user[0]
        host = event.source().host
        msg = event.arguments()[0]

        if self._iscmd(msg):
            resp = self._process_cmd(conn, event, public, msg)

            if public:
                target = self.channel
            else:
                target = nick

            self._send_response(conn, resp, target)

        if public:
            # Create a log entry
            plugins.logs.create_entry(nick, user, host, msg)



