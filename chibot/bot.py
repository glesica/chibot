"""
An IRC bot for the Chicago GLUG channel.
"""
import sys
import datetime
import threading
import Queue as queue
import irc.bot
from . import messages
from . import plugins


class ChiBot(irc.bot.SingleServerIRCBot):
    def __init__(self, nickname, channel, server, port=6667):
        irc.bot.SingleServerIRCBot.__init__(
            self,
            [(server, port)],
            nickname,
            nickname
        )
        self.channel = channel
        self.response_queue = queue.Queue()
        self.request_stop = threading.Event()

    def on_nicknameinuse(self, conn, event):
        conn.nick(conn.get_nickname() + "_")

    def on_welcome(self, conn, event):
        conn.join(self.channel)

    def on_privmsg(self, conn, event):
        msg = messages.Message(event, public=False)
        self.process_message(msg)

    def on_pubmsg(self, conn, event):
        msg = messages.Message(event, public=True)
        self.process_message(msg)

    # Custom methods

    def process_message(self, message):
        """
        Processes an incoming message by spawning a thread 
        for each available plugin.
        """
        for plugin in plugins.registered_plugins:
            args = (
                plugin, 
                message, 
                self.response_queue,
            )
            t = threading.Thread(
                target=self.run_plugin,
                args=args
            )
            t.start()

    @staticmethod
    def run_plugin(plugin, message, response_queue):
        """
        Runs the given plugin and places the result into the 
        queue provided.
        """
        try:
            resp = plugin(message)
        except Exception, e:
            #TODO: Log the error with some info about it
            resp = plugins.Response('Plugin error') # This is silent
        finally:
            if resp:
                response_queue.put(resp)

    @staticmethod
    def process_responses(response_queue, connection, stop_event):
        """
        Consumes responses from the given queue and sends them 
        to the IRC connection given.
        """
        while not stop_event.is_set():
            try:
                resp = response_queue.get(timeout=1)
            except queue.Empty:
                continue
            for line in resp:
                if resp.response_type == plugins.NORMAL_RESPONSE:
                    connection.privmsg(resp.target, line)
                if resp.response_type == plugins.NOTICE_RESPONSE:
                    connection.notice(resp.target, line)
            response_queue.task_done()
