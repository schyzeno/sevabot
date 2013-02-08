# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import sys
import logging
import hashlib
import time
from collections import OrderedDict
import Skype4Py
import shlex

from sevabot.bot import modules

logger = logging.getLogger("sevabot")


class Sevabot:
    """
    Skype bot interface handler.
    """

    def __init__(self):
        self.cmds = {}
        self.chats = {}

    def start(self):

        if sys.platform == "linux2":
            self.skype = Skype4Py.Skype(Transport='x11')
        else:
            # OSX
            self.skype = Skype4Py.Skype()

        logger.debug("Attaching to Skype")
        self.skype.Attach()

        logger.debug("Skype API connection established")
        self.skype.OnMessageStatus = self.handleMessages

        self.cacheChats()

    def cacheChats(self):
        """
        Scan all chats on initial connect.
        """
        logger.debug("Async cacheChats() -- this may take a while")
        self.chats = OrderedDict()

        # First get all fresh chats
        chats = []
        for chat in self.skype.Chats:

            # filter chats older than 6 months
            if time.time() - chat.ActivityTimestamp > 3600 * 24 * 180:
                continue

            chats.append(chat)

        chats = sorted(chats, key=lambda c: c.ActivityTimestamp, reverse=True)

        for chat in chats:
            # Encode ids in b64 so they are easier to pass in URLs
            m = hashlib.md5()
            m.update(chat.Name)
            self.chats[m.hexdigest()] = chat

    def getOpenChats(self):
        """
        Get list of id -> chat object of all chats which are open.
        """

        # Make sure we get refresh chat list every time
        self.cacheChats()
        for chat_id, chat in self.chats.items():
            yield chat_id, chat

    def handleMessages(self, msg, status):
        """
        Handle incoming messages
        """
        if status == "RECEIVED" or status == "SENT":
            logger.debug("%s - %s - %s: %s" % (status, msg.Chat.FriendlyName, msg.FromHandle, msg.Body))

        if status in ["RECEIVED", "SENT"] and msg.Body:

            body = msg.Body.encode("utf-8")

            # shlex dies on unicode on OSX with null bytes all over the string
            words = shlex.split(body, comments=False, posix=True)

            if len(words) < 0:
                return

            keyword = words[0]

            if not keyword.startswith("!"):
                return

            keyword = keyword[1:]

            logger.debug("Trying to identify keyword: %s" % keyword)

            # reload must be built in
            if keyword == "reload":
                commands = modules.load_modules()
                msg.Chat.SendMessage("Available commands: %s" % ", ".join(commands))
                return

            if modules.is_module(keyword):
                # Execute module asynchronously

                def callback(output):
                    msg.Chat.SendMessage(output)

                modules.run_module(keyword, words[1:], callback)
                return
            else:
                msg.Chat.SendMessage("Don't know about command: !" + keyword)

            # XXX: Deprecated. See if we can rid of this
            if body == "!loadChats":
                self.cacheChats()
                return

    def sendMsg(self, chat, msg):
        """
        Send a message to chat.

        :param chat: Chat id as a string

        :param msg: Message as UTF-8 encoded string
        """
        try:
            self.chats[chat].SendMessage(msg)
            return "Message sent\n"
        except KeyError:
            raise RuntimeError("No chat %s" % chat)
