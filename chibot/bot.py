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
        self.process_message(conn, event, public=False)

    def on_pubmsg(self, conn, event):
        self.process_message(conn, event, public=True)
        return
        a = e.arguments()[0].split(":", 1)
        if len(a) > 1 and irc_lower(a[0]) == irc_lower(self.connection.get_nickname()):
            self.process_message(e, a[1].strip(), public=Truevent)

    # Custom methods

    def _iscmd(self, conn, msg, public):
        if not public:
            return True

        return msg.startswith(conn.get_nickname() + ':')

    def _process_cmd(self, cmd, args):
        print plugins.registered_plugins #DEBUG
        
        if cmd not in plugins.registered_plugins:
            return plugins.NoticeResponse('Unknown command: %s' % cmd)
            
        func = plugins.registered_plugins[cmd]
        try:
            return func(cmd, *args)
        except Exception, e:
            print e #DEBUG
            return plugins.NoticeResponse('There were some problems, command failed horribly.')

    def process_message(self, conn, event, public=False):
        nick = event.source().nick
        user = event.source().user[0]
        host = event.source().host
        msg = event.arguments()[0]

        if self._iscmd(conn, msg, public):
            # parse command and run
            if public:
                cs = msg.split(':', 1)[1]
            else:
                cs = msg

            cmd = cs.split()[0]
            args = cs.split()[1:]
            resp = self._process_cmd(cmd, args)

            if public:
                target = self.channel
            else:
                target = nick

            for line in resp:
                if resp.response_type == plugins.NORMAL_RESPONSE:
                    conn.privmsg(target, line)
                if resp.response_type == plugins.NOTICE_RESPONSE:
                    conn.notice(target, line)


        if public:
            # Create a log entry
            plugins.logs.create_entry(nick, user, host, msg)



